from django.db import models
from camera_manager.models import (
	Location,
    Camera,
)

class IncidentType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, default=None)

class Incident(models.Model):
   timestamp = models.DateTimeField(auto_now_add=True)
   camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
   incident_type = models.ForeignKey(IncidentType, on_delete=models.CASCADE)
   link = models.URLField(blank=True, default=None)

class ZoneStat(models.Model):
   timestamp = models.DateTimeField(auto_now_add=True)
   location = models.ForeignKey(Location, on_delete=models.CASCADE, default='0')
   value = models.IntegerField(default=0)
   change = models.IntegerField(default=0)

   def __str__(self):
       return self.location
   
class CameraStat(models.Model):
   timestamp = models.DateTimeField(auto_now_add=True)
   camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
   input_value = models.IntegerField()
   output_value = models.IntegerField()

   def __str__(self):
       return self.camera.camera_name
