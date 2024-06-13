from django.db import models
from camera_manager.models import (
	Location,
    Camera,
)
from django.contrib.auth.models import User


class IncidentType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, default=None)

class Incident(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('closed', 'Закрыто'),
    ]
   
    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField(default=None, null=True, blank=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    incident_type = models.ForeignKey(IncidentType, on_delete=models.CASCADE)
    link = models.URLField(blank=True, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents', default=1)

class ZoneStat(models.Model):
   timestamp = models.DateTimeField()
   location = models.ForeignKey(Location, on_delete=models.CASCADE)
   value = models.IntegerField(default=0)
   change = models.IntegerField(default=0)

   def __str__(self):
       return f'{self.location.location} - {self.timestamp}'
   
class CameraStat(models.Model):
   timestamp = models.DateTimeField()
   camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
   input_value = models.IntegerField()
   output_value = models.IntegerField()

   def __str__(self):
       return self.camera.camera_name
