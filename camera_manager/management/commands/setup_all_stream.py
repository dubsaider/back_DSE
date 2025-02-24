from django.core.management.base import BaseCommand
from camera_manager.models import Camera
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Setup all cameras by creating Kubernetes resources and sending configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--container-image',
            type=str,
            default='alexxit/go2rtc:1.9.8',
            help='Container image to use (default: alexxit/go2rtc)',
        )

    def handle(self, *args, **kwargs):
        container_image = kwargs['container_image']

        logger.info('Setting up all cameras...')

        try:
            cameras = Camera.objects.all()
            if not cameras.exists():
                logger.warning('No cameras found in the database.')
                self.stdout.write(self.style.WARNING('No cameras found in the database.'))
                return

            for camera in cameras:
                logger.info(f'Setting up camera {camera.id}...')
                try:
                    call_command(
                        'setup_stream',
                        str(camera.id),
                        container_image=container_image
                    )
                    logger.info(f'Camera {camera.id} setup completed successfully.')
                except Exception as e:
                    logger.error(f'[ERROR] Failed to setup camera {camera.id}: {e}')
                    self.stdout.write(self.style.ERROR(f'Failed to setup camera {camera.id}: {e}'))

            self.stdout.write(self.style.SUCCESS('All cameras have been set up.'))
            logger.info('All cameras have been set up.')

        except Exception as e:
            logger.error(f'[ERROR] Failed to setup all cameras: {e}')
            self.stdout.write(self.style.ERROR(f'Failed to setup all cameras: {e}'))