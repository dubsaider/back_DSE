from django.db import models
from camera_manager.models import (
	Camera,
	CameraGroup,
	Location
)

class CameraToGroup(models.Model):
	group_id = models.ForeignKey(CameraGroup, on_delete=models.CASCADE)
	camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)

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
