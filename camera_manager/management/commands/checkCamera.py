from django.core.management.base import BaseCommand
from camera_manager.models import Camera
from api.models import Incident, IncidentType
import requests
from datetime import datetime

class CameraCheckCommand(BaseCommand):
    help = "Updating camera status data in the database"

    def get_incident_type(self, is_active):
        return IncidentType.objects.get(name='Изменение статуса камеры на "Активный"') if is_active else IncidentType.objects.get(name='Изменение статуса камеры на "Неактивный"')

    def handle(self, *args, **kwargs):
        try:
            incident_type_active = self.get_incident_type(True)
            incident_type_inactive = self.get_incident_type(False)
        except IncidentType.DoesNotExist as e:
            self.stderr.write(self.style.ERROR('IncidentType does not exist: {}'.format(e)))
            return

        for obj in Camera.objects.all():
            ip = obj.camera_ip
            status = obj.is_active
            new_status = False

            with requests.Session() as session:
                try:
                    response = session.get(f"http://{ip}:554", timeout=5)
                    new_status = response.ok
                except requests.exceptions.Timeout:
                    self.stderr.write(self.style.WARNING('Camera check timed out: {}'.format(ip)))
                    new_status = False
                except requests.exceptions.ConnectionError:
                    self.stderr.write(self.style.WARNING('Camera connection error: {}'.format(ip)))
                    new_status = True
                except requests.exceptions.RequestException as e:
                    if hasattr(e, 'response') and e.response.status_code ==  401:
                        self.stderr.write(self.style.WARNING('Camera requires authorization: {}'.format(ip)))
                        new_status = True
                    else:
                        self.stderr.write(self.style.WARNING('Camera check failed: {}'.format(e)))
                        new_status = False


            if status != new_status:
                incident_type = incident_type_active if status else incident_type_inactive
                new_incident_type = incident_type_active if new_status else incident_type_inactive

                new_incident = Incident(
                    camera=obj,
                    incident_type=new_incident_type,
                    link=""
                )
                new_incident.save()

                Camera.objects.filter(pk=obj.pk).update(is_active=new_status)