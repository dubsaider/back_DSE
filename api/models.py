from django.db import models
from camera_manager.models import (
	Location,
    Camera,
)

class DetectedObjectType(models.Model):
	type = models.CharField(max_length=255)
	description = models.CharField(max_length=255, null=True)

	def __str__(self):
		return self.type

class ObjectsDetectionLog(models.Model):
	datestamp = models.DateTimeField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	type = models.ForeignKey(DetectedObjectType, on_delete=models.CASCADE)
	count = models.IntegerField(default=0)

class IncidentType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, default=None)

class Incident(models.Model):
   timestamp = models.DateTimeField(auto_now_add=True)
   camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
   incident_type = models.ForeignKey(IncidentType, on_delete=models.CASCADE)
   link = models.URLField(blank=True, default=None)

class ZoneStats(models.Model):
   timestamp = models.DateTimeField(auto_now_add=True)
   camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
   location = models.ForeignKey(Location, on_delete=models.CASCADE)
   change = models.IntegerField()

   def __str__(self):
       return self.location
