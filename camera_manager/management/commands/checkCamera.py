from django.core.management.base import BaseCommand
from camera_manager.models import Camera
from api.models import Incident
import requests
from datetime import datetime


class CameraCheckCommand(BaseCommand):
    help = "Updating camera status data in the database"

    def handle(self, *args, **kwargs):
        for obj in Camera.objects.all():
            ip = obj.camera_ip
            status = obj.is_active
            new_status = False
            try:
                requests.get(f"http://{ip}:554", timeout=1)
            except requests.exceptions.Timeout:
                new_status = False
            except requests.exceptions.ConnectionError:
                new_status = True
            res_1 = "active" if status else "inactive"
            res_2 = "active" if new_status else "inactive"
            if res_1 != res_2:               
                new_incedent = Incident(
                    camera=obj,
                    event=f"Изменился статус камеры",
                    incident=f"Камера имела статус {res_1}, теперь имеет - {res_2}",
                    link=""
                )
                new_incedent.save()
                obj.is_active = new_status
                obj.save()

