from django.core.management.base import BaseCommand
from camera_manager.models import Camera
import logging
import subprocess

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start streams for all active cameras'

    def handle(self, *args, **kwargs):
        cameras = Camera.objects.filter(is_active=True)

        for camera in cameras:
            logger.info(f'Setting up stream for camera {camera.id}...')
            try:
                subprocess.run(['python', 'manage.py', 'setup_stream', str(camera.id)], check=True)
                self.stdout.write(self.style.SUCCESS(f'Successfully set up stream for camera {camera.id}'))
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to set up stream for camera {camera.id}: {e}")
                self.stdout.write(self.style.ERROR(f'Failed to set up stream for camera {camera.id}'))

        self.stdout.write(self.style.SUCCESS('Successfully set up streams for all active cameras'))
        logger.info('Streams setup completed for all active cameras.')