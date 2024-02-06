from django.apps import AppConfig


class CameraManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'camera_manager'

    def ready(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from .views import update_previews
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_previews, 'interval', minutes=10)
        scheduler.start()
