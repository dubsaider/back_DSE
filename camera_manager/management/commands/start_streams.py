import logging
import time
from django.core.management.base import BaseCommand
from kubernetes import client, config
from utils.k8s_utils import initialize_k8s_api
from camera_manager.models import Camera, Stream
import requests
from back.settings import K8S_ADDRESS

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start streams for all active cameras'

    def add_arguments(self, parser):
        max_cameras = Camera.objects.filter(is_active=True).count()
        parser.add_argument('--max_cameras', type=int, default=max_cameras, help='Maximum number of cameras to start streams for')
        parser.add_argument('--stream_per_node', type=int, default=1, help='Number of streams per container')

    def handle(self, *args, **kwargs):
        max_cameras = kwargs['max_cameras']
        stream_per_node = kwargs['stream_per_node']
        logger.info(f'Starting streams for up to {max_cameras} active cameras with {stream_per_node} streams per container...')

        k8s_api = initialize_k8s_api()

        cameras = self.get_active_cameras(max_cameras)

        self.create_pods_and_services(k8s_api, cameras, stream_per_node)

        self.wait_for_pods_ready(k8s_api, cameras)

        self.start_streams(k8s_api, cameras)

        logger.info('Successfully started streams for all active cameras')

    def get_active_cameras(self, max_cameras):
        return Camera.objects.filter(is_active=True)[:max_cameras]

    def create_pods_and_services(self, k8s_api, cameras, stream_per_node):
        for i in range(0, len(cameras), stream_per_node):
            camera_batch = cameras[i:i + stream_per_node]
            try:
                self.create_pod_and_service(k8s_api, camera_batch)
            except Exception as e:
                logger.error(f"Failed to create pod and service for camera batch: {e}")

    def create_pod_and_service(self, k8s_api, camera_batch):
        for camera in camera_batch:
            if not Stream.objects.filter(camera=camera).exists():
                try:
                    self.create_pod(k8s_api, camera)
                    self.create_service(k8s_api, camera)
                except Exception as e:
                    logger.error(f"Failed to create pod and service for camera {camera.id}: {e}")

    def create_pod(self, k8s_api, camera):
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': f"stream-{camera.id}",
                'labels': {
                    'app': 'stream',
                    'camera_id': str(camera.id)
                }
            },
            'spec': {
                'containers': [{
                    'name': 'streaming-unit-image',
                    'image': 'dubsaider/streaming-unit-image:latest',
                    'env': [
                        {'name': 'SECRET_KEY', 'valueFrom': {'secretKeyRef': {'name': 'django-secret-key', 'key': 'SECRET_KEY'}}},
                        {'name': 'USER_KEY', 'valueFrom': {'secretKeyRef': {'name': 'kuber-certs', 'key': 'user-key'}}},
                        {'name': 'CA_CERT', 'valueFrom': {'secretKeyRef': {'name': 'kuber-certs', 'key': 'ca-crt'}}},
                        {'name': 'USER_CERT', 'valueFrom': {'secretKeyRef': {'name': 'kuber-certs', 'key': 'user-crt'}}},
                        {'name': 'K8S_ADDRESS', 'value': K8S_ADDRESS},
                        {'name': 'DEBUG', 'value': str(True)},
                        {'name': 'CORS_ORIGIN_ALLOW_ALL', 'value': str(True)}
                    ],
                    'ports': [
                        client.V1ContainerPort(
                            container_port=80,
                            protocol='TCP'
                        )
                    ],
                }]
            }
        }
        k8s_api.create_namespaced_pod(namespace='default', body=pod_manifest)

    def create_service(self, k8s_api, camera):
        service_manifest = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"stream-service-{camera.id}",
                'labels': {
                    'app': 'stream',
                    'camera_id': str(camera.id)
                }
            },
            'spec': {
                'selector': {
                    'app': 'stream',
                    'camera_id': str(camera.id)
                },
                'ports': [
                    {
                        'protocol': 'TCP',
                        'port': 80,
                        'targetPort': 8000
                    }
                ],
                'type': 'NodePort'
            }
        }
        k8s_api.create_namespaced_service(namespace='default', body=service_manifest)

    def wait_for_pods_ready(self, k8s_api, cameras):
        for camera in cameras:
            try:
                self.wait_for_pod_ready(k8s_api, f"stream-{camera.id}")
            except Exception as e:
                logger.error(f"Failed to start pod for camera {camera.id}: {e}")

    def wait_for_pod_ready(self, k8s_api, pod_name):
        for _ in range(60):
            pod = k8s_api.read_namespaced_pod(name=pod_name, namespace='default')
            if pod.status.phase == 'Running':
                return
            time.sleep(1)
        raise Exception(f"Pod {pod_name} did not start in time.")

    def start_streams(self, k8s_api, cameras):
        for camera in cameras:
            try:
                self.start_stream_for_camera(k8s_api, camera)
            except Exception as e:
                logger.error(f"Failed to start stream for camera {camera.id}: {e}")

    def start_stream_for_camera(self, k8s_api, camera):
        if not Stream.objects.filter(camera=camera).exists():
            service_name = f"stream-service-{camera.id}"
            try:
                k8s_api.read_namespaced_service(name=service_name, namespace='default')
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    logger.error(f"Service {service_name} does not exist for camera {camera.id}")
                    return
                else:
                    logger.error(f"Failed to read service {service_name} for camera {camera.id}: {e}")
                    return

            try:
                service = k8s_api.read_namespaced_service(name=service_name, namespace='default')
                node_port = service.spec.ports[0].node_port
                response_status = self.start_stream(camera, node_port)
                if response_status != 200:
                    self.delete_pod_and_service(k8s_api, f"stream-{camera.id}", service_name)
                    return
                Stream.objects.create(camera=camera, k8s_pod_name=f"stream-{camera.id}", k8s_pod_port=node_port)
            except Exception as e:
                logger.error(f"Failed to start stream for camera {camera.id}: {e}")
                self.delete_pod_and_service(k8s_api, f"stream-{camera.id}", service_name)

    def start_stream(self, camera, node_port):
        stream_url = f"http://{K8S_ADDRESS}:{node_port}/convert_to_hls/streams/{camera.id}/start/?ip={camera.camera_ip}&port=554&channel=101&resolution=720p"
        response = requests.get(stream_url)
        if response.status_code != 200:
            logger.error(f"Failed to start stream for camera {camera.id}: {response.text}")
            raise Exception(f"Failed to start stream for camera {camera.id}: {response.text}")
        return response.status_code

    def delete_pod_and_service(self, k8s_api, pod_name, service_name):
        try:
            k8s_api.delete_namespaced_pod(name=pod_name, namespace='default')
            logger.info(f"Pod {pod_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to delete pod {pod_name}: {e}")

        try:
            k8s_api.delete_namespaced_service(name=service_name, namespace='default')
            logger.info(f"Service {service_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to delete service {service_name}: {e}")