from django.apps import AppConfig

class CameraManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'camera_manager'

    def ready(self):
        from .tasks import start_camera_checks
        start_camera_checks()