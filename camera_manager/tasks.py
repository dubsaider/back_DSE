from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def start_camera_checks():
    scheduler = BackgroundScheduler()
    scheduler.add_job(call_command, 'interval', minutes=5, args=['check_cameras'])
    scheduler.start()