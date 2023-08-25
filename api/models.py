from django.db import models


class Camera(models.Model):
	camera_name = models.CharField(max_length=255)
	camera_ip = models.CharField(max_length=15)
	camera_description = models.CharField(max_length=255)
	
class ClusterUnit(models.Model):
	unit_name = models.CharField(max_length=255)
	unit_ip = models.CharField(max_length=15)
	unit_config = models.JSONField()
	
class Processing(models.Model):
	camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
	unit = models.ForeignKey(ClusterUnit, on_delete=models.CASCADE)
	processing_config = models.JSONField()
	result_link = models.URLField(blank=True, null=True)

class Locations(models.Model):
	location = models.CharField(max_length=255)

class DetectedObjectTypes(models.Model):
	type = models.CharField(max_length=255)

class ObjectsDetectionLogs(models.Model):
	datestamp = models.DateTimeField()
	location = models.ForeignKey(Locations, on_delete=models.CASCADE)
	type = models.ForeignKey(DetectedObjectTypes, on_delete=models.CASCADE)
	count = models.IntegerField(default=0)
