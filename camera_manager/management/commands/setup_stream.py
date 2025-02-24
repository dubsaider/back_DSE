from django.core.management.base import BaseCommand
from camera_manager.models import Camera, Stream
from utils.k8s_utils import (
    get_k8s_apis,
    get_secrets,
    create_pod,
    create_service,
    create_ingress,
    delete_pod,
    delete_service,
    delete_ingress,
    client
)
import yaml
import requests
import logging
import time
from back.settings import K8S_ADDRESS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Setup a camera by creating Kubernetes resources and sending configuration'

    def add_arguments(self, parser):
        parser.add_argument('camera_id', type=int, help='ID of the camera to setup')
        parser.add_argument(
            '--container-image',
            type=str,
            default='alexxit/go2rtc:1.9.8',
            help='Container image to use (default: alexxit/go2rtc)',
        )

    def handle(self, *args, **kwargs):
        camera_id = kwargs['camera_id']
        container_image = kwargs['container_image']

        camera = Camera.objects.get(id=camera_id)

        core_v1_api, _, networking_api = get_k8s_apis()

        logger.info(f'Setting up camera {camera.id}...')

        try:
            self.create_k8s_resources(core_v1_api, networking_api, camera, container_image)

            secret_name = f"camera-secret-{camera.id}"
            namespace = 'default'
            login, password = get_secrets(core_v1_api, secret_name, namespace)
            if not login or not password:
                logger.error(f'[ERROR] Failed to retrieve secrets for camera {camera.id}. Skipping...')
                return

            stream_url = f'rtsp://{login}:{password}@{camera.camera_ip}:554/ISAPI/Streaming/Channels/101'

            config = self.generate_config(camera, stream_url)

            self.send_config_to_pod(camera, config)

            self.create_stream_record(camera)

            self.stdout.write(self.style.SUCCESS(f'Successfully set up camera {camera.id}'))
            logger.info(f'Camera {camera.id} setup completed.')

        except Exception as e:
            logger.error(f'[ERROR] Failed to setup camera {camera.id}: {e}')
            self.cleanup_resources(core_v1_api, networking_api, camera)

    def generate_config(self, camera, stream_url):
        return {
            'server': {
                'address': '0.0.0.0:1984',
            },
            'websocket': {
                'check_origin': False,
            },
            'http': {
                'listen': ':1984',
                'root': '/app/static',
                'cors': {
                    'allow_origin': '*',
                    'allow_methods': 'GET, POST, OPTIONS',
                    'allow_headers': 'Content-Type',
                },
                'websocket': {
                    'check_origin': False,
                },
            },
            'streams': {
                f'camera-{camera.id}': stream_url
            },
            'log': {
                'level': 'debug',
                'file': '/var/log/go2rtc.log',
            },
            'hls': {
                'dir': '/var/www/html/hls',
                'segment_duration': 5,
                'segment_time': 5,
                'playlist_length': 2,
                'keepalive': True,
            },
            'api': {
                'origin': '*'
            }
        }

    def create_k8s_resources(self, core_v1_api, networking_api, camera, container_image):
        """Создает необходимые ресурсы Kubernetes для Pod."""
        pod_manifest = self.get_pod_manifest(camera, container_image)
        service_manifest = self.get_service_manifest(camera)

        create_pod(core_v1_api, pod_manifest)

        create_service(core_v1_api, service_manifest)

        create_ingress(networking_api, camera)

    def get_pod_manifest(self, camera, container_image):
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': f"go2rtc-pod-{camera.id}",
                'labels': {
                    'app': f'go2rtc-{camera.id}'
                }
            },
            'spec': {
                'containers': [{
                    'name': 'go2rtc',
                    'image': container_image,
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
                'name': f"go2rtc-{camera.id}-service"
            },
            'spec': {
                'selector': {
                    'app': f'go2rtc-{camera.id}'
                },
                'ports': [
                    {
                        'protocol': 'TCP',
                        'port': 80,
                        'targetPort': 1984,
                        'nodePort': 0
                    }
                ],
                'type': 'NodePort'
            }
        }

    def send_config_to_pod(self, camera, config):
        """Отправляет конфигурацию в Pod через Ingress в формате YAML после его запуска."""
        ingress_host = f"http://{K8S_ADDRESS}:31163/cameras/go2rtc-{camera.id}"
        core_v1_api, _, _ = get_k8s_apis()

        try:
            if not self.wait_for_pod_ready(core_v1_api, camera):
                logger.error(f"Pod for camera {camera.id} did not become ready in time.")
                return

            config_yaml = yaml.dump(config)

            config_url = f"{ingress_host}/api/config"
            config_headers = {
                "Content-Type": "text/plain;charset=UTF-8",
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "Origin": f"http://{K8S_ADDRESS}:1984",
                "Referer": f"http://{K8S_ADDRESS}:1984/editor.html"
            }

            if not self.retry_request("POST", config_url, data=config_yaml, headers=config_headers, max_attempts=5, delay=5):
                logger.error(f"Failed to send config to pod for camera {camera.id} after multiple attempts.")
                return

            restart_url = f"{ingress_host}/api/restart"
            restart_headers = {
                "Content-Type": "application/json",
                "Accept": "*/*"
            }

            if not self.retry_request("POST", restart_url, headers=restart_headers, max_attempts=5, delay=5):
                logger.error(f"Failed to restart application for camera {camera.id} after multiple attempts.")
                return

        except Exception as e:
            logger.error(f"Failed to send config or restart pod for camera {camera.id}: {e}")


    def wait_for_pod_ready(self, core_v1_api, camera, timeout=120, interval=5):
        """Ожидает, пока Pod станет доступным."""
        pod_name = f"go2rtc-pod-{camera.id}"
        namespace = "default"
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                pod = core_v1_api.read_namespaced_pod(name=pod_name, namespace=namespace)
                if pod.status.phase == "Running" and self.is_pod_ready(pod):
                    logger.info(f"Pod {pod_name} is ready.")
                    return True
            except client.exceptions.ApiException as e:
                if e.status != 404:
                    logger.warning(f"Error checking pod status: {e}")
            time.sleep(interval)

        logger.error(f"Timed out waiting for pod {pod_name} to become ready.")
        return False


    def is_pod_ready(self, pod):
        """Проверяет, готов ли Pod."""
        for condition in pod.status.conditions or []:
            if condition.type == "Ready" and condition.status == "True":
                return True
        return False


    def retry_request(self, method, url, **kwargs):
        """Выполняет повторные попытки HTTP-запроса."""
        max_attempts = kwargs.pop("max_attempts", 5)
        delay = kwargs.pop("delay", 5)

        for attempt in range(max_attempts):
            try:
                response = requests.request(method, url, **kwargs)
                if response.status_code == 200:
                    logger.info(f"Successfully executed request to {url}.")
                    return True
                else:
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts}: Failed to execute request to {url}. Status code: {response.status_code}. Response: {response.text}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_attempts}: Request failed: {e}")

            if attempt < max_attempts - 1:
                time.sleep(delay)

        logger.error(f"Failed to execute request to {url} after {max_attempts} attempts.")
        return False

    def create_stream_record(self, camera):
        """Создает запись о потоке в базе данных."""
        service_name = f"go2rtc-{camera.id}-service"
        core_v1_api, _, _ = get_k8s_apis()
        service = core_v1_api.read_namespaced_service(name=service_name, namespace='default')
        cluster_ip = service.spec.cluster_ip
        
        if Stream.objects.filter(camera=camera).exists():
            logger.info(f"Stream record for camera {camera.id} already exists. Skipping creation.")
            return

        Stream.objects.create(
            camera=camera,
            k8s_pod_name=f"go2rtc-pod-{camera.id}",
            k8s_pod_port=80,
            status='running'
        )
        logger.info(f"Created Stream record for camera {camera.id}")

    def cleanup_resources(self, core_v1_api, networking_api, camera):
        """Очищает созданные ресурсы при ошибке."""
        logger.warning(f'Cleaning up resources for camera {camera.id}...')
        delete_pod(core_v1_api, f"go2rtc-pod-{camera.id}")
        delete_service(core_v1_api, f"go2rtc-{camera.id}-service")
        delete_ingress(networking_api, camera.id)