from django.apps import AppConfig


class CameraManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'camera_manager'
    
    def ready(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from .management.commands.checkCamera import CameraCheckCommand

        cameraChecker = CameraCheckCommand()
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(cameraChecker.handle, 'interval', minutes=15)
        scheduler.start()
    
