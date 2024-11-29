from django.core.management.base import BaseCommand
from camera_manager.models import Camera, Stream
from utils.k8s_utils import initialize_k8s_api, get_secrets
import logging
import subprocess
import os
import yaml

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup a camera by creating Kubernetes resources and sending configuration'

    def add_arguments(self, parser):
        parser.add_argument('camera_id', type=int, help='ID of the camera to setup')

    def handle(self, *args, **kwargs):
        camera_id = kwargs['camera_id']
        camera = Camera.objects.get(id=camera_id)
        k8s_api = initialize_k8s_api()

        logger.info(f'Setting up camera {camera.id}...')

        self.generate_config(camera, k8s_api)

        self.create_k8s_resources(camera)

        self.send_config_to_pod(camera)

        self.create_stream_record(camera)

        self.stdout.write(self.style.SUCCESS(f'Successfully set up camera {camera.id}'))
        logger.info(f'Camera {camera.id} setup completed.')

    def generate_config(self, camera, k8s_api):
        subprocess.run(['python', 'manage.py', 'generate_go2rtc_config', str(camera.id)], check=True)

    def create_k8s_resources(self, camera):
        deployment_manifest = self.get_deployment_manifest(camera)
        service_manifest = self.get_service_manifest(camera)

        with open('deployment_manifest.yaml', 'w') as file:
            yaml.dump(deployment_manifest, file, default_flow_style=False)

        with open('service_manifest.yaml', 'w') as file:
            yaml.dump(service_manifest, file, default_flow_style=False)

        subprocess.run(['python', 'manage.py', 'create_k8s_resources', 'deployment_manifest.yaml'], check=True)
        subprocess.run(['python', 'manage.py', 'create_k8s_resources', 'service_manifest.yaml'], check=True)

        pod_name = f"go2rtc-pod-{camera.id}"
        subprocess.run(['python', 'manage.py', 'wait_for_pod_ready', pod_name], check=True)

    def get_deployment_manifest(self, camera):
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': f"go2rtc-pod-{camera.id}",
                'labels': {
                    'app': 'go2rtc',
                    'camera_id': str(camera.id)
                }
            },
            'spec': {
                'containers': [{
                    'name': 'go2rtc',
                    'image': 'vilams/go2rtc:1.0',
                    'ports': [
                        {'containerPort': 1984}
                    ]
                }]
            }
        }

    def get_service_manifest(self, camera):
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"go2rtc-service-{camera.id}",
                'labels': {
                    'app': 'go2rtc',
                    'camera_id': str(camera.id)
                }
            },
            'spec': {
                'selector': {
                    'app': 'go2rtc',
                    'camera_id': str(camera.id)
                },
                'ports': [
                    {
                        'port': 1984,
                        'targetPort': 1984
                    }
                ],
                'type': 'NodePort'
            }
        }

    def send_config_to_pod(self, camera):
        pod_name = f"go2rtc-pod-{camera.id}"
        subprocess.run(['python', 'manage.py', 'send_config_to_pod', pod_name, str(camera.id)], check=True)

    def create_stream_record(self, camera):
        service_name = f"go2rtc-service-{camera.id}"
        k8s_api = initialize_k8s_api()
        service = k8s_api.read_namespaced_service(name=service_name, namespace='default')
        node_port = service.spec.ports[0].node_port

        Stream.objects.create(
            camera=camera,
            k8s_pod_name=f"go2rtc-pod-{camera.id}",
            k8s_pod_port=node_port,
            status='running'
        )
        logger.info(f"Created Stream record for camera {camera.id}")