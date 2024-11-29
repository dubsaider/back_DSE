from django.core.management.base import BaseCommand
from camera_manager.models import Camera
from utils.k8s_utils import initialize_k8s_api, get_secrets
import logging
import yaml
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate go2rtc.yaml configuration file based on Camera model'

    def add_arguments(self, parser):
        parser.add_argument('camera_id', type=int, help='ID of the camera to generate config for')

    def handle(self, *args, **kwargs):
        camera_id = kwargs['camera_id']
        camera = Camera.objects.get(id=camera_id)
        k8s_api = initialize_k8s_api()

        secret_name = f"camera-secret-{camera.id}"
        namespace = 'default'
        login, password = get_secrets(k8s_api, secret_name, namespace)
        if not login or not password:
            logger.error(f'[ERROR] Failed to retrieve secrets for camera {camera.id}. Skipping...')
            return

        stream_name = f'stream{camera.pk}'
        stream_url = f'rtsp://{login}:{password}@{camera.camera_ip}:554/ISAPI/Streaming/Channels/101'

        config = {
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
                stream_name: [stream_url]
            },
            'log': {
                'level': 'info',
                'file': '/var/log/go2rtc.log',
            },
            'hls': {
                'dir': '/var/www/html/hls',
                'segment_duration': 10,
                'playlist_length': 5,
                'keepalive': True,
            },
        }

        config_str = yaml.dump(config, default_flow_style=False)
        config_file_path = os.path.join('configs', f'go2rtc-stream{camera.pk}.yaml')
        with open(config_file_path, 'w') as file:
            file.write(config_str)

        self.stdout.write(self.style.SUCCESS(f'Successfully generated config for camera {camera_id}'))
        logger.info(f'Config generation completed for camera {camera_id}.')

        return config_str