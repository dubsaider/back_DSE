from django.core.management.base import BaseCommand
from utils.k8s_utils import initialize_k8s_api
import logging
import requests
from back.settings import K8S_ADDRESS
import asyncio
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send configuration to a specific pod and restart the application'

    def add_arguments(self, parser):
        parser.add_argument('pod_name', type=str, help='Name of the pod to send the config to')
        parser.add_argument('camera_id', type=int, help='ID of the camera')

    def handle(self, *args, **kwargs):
        pod_name = kwargs['pod_name']
        camera_id = kwargs['camera_id']
        k8s_api = initialize_k8s_api()

        config_file_path = os.path.join('configs', f'go2rtc-stream{camera_id}.yaml')
        with open(config_file_path, 'r') as file:
            config = file.read()

        asyncio.run(self.send_config_to_pod(k8s_api, pod_name, config))

        self.stdout.write(self.style.SUCCESS(f'Successfully sent config to pod {pod_name}'))
        logger.info(f'Config sent to pod {pod_name}.')

    async def send_config_to_pod(self, k8s_api, pod_name, config):
        try:
            service_name = f"go2rtc-service-{pod_name.split('-')[-1]}"
            service = await asyncio.to_thread(k8s_api.read_namespaced_service, name=service_name, namespace='default')
            service_port = service.spec.ports[0].node_port
            config_url = f"http://{K8S_ADDRESS}:{service_port}/api/config"
            restart_url = f"http://{K8S_ADDRESS}:{service_port}/api/restart"

            try:
                response = await asyncio.to_thread(requests.post, config_url, data=config, headers={'Content-Type': 'application/yaml'})
                if response.status_code == 200:
                    logger.info(f"Successfully sent config to pod {pod_name}")
                else:
                    logger.error(f"Failed to send config to pod {pod_name}: {response.text}")

                restart_response = await asyncio.to_thread(requests.post, restart_url)
                if restart_response.status_code == 200:
                    logger.info(f"Successfully restarted application in pod {pod_name}")
                else:
                    logger.error(f"Failed to restart application in pod {pod_name}: {restart_response.text}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send config or restart application in pod {pod_name}: {e}")
        except Exception as e:
            logger.error(f"Failed to read service {service_name} for camera {pod_name}: {e}")