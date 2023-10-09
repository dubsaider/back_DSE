from django.db import models


class Location(models.Model):
	location = models.CharField(max_length=255)

	def __str__(self):
		return self.location

class Camera(models.Model):
	camera_name = models.CharField(max_length=255)
	camera_ip = models.CharField(max_length=15)
	input_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='imput_location')
	output_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='output_location')
	camera_description = models.CharField(max_length=255)

	def __str__(self):
		return self.camera_name
	
class ClusterUnit(models.Model):
	unit_name = models.CharField(max_length=255)
	unit_ip = models.CharField(max_length=15)
	unit_config = models.JSONField()

	def __str__(self):
		return self.unit_name
	
class Processing(models.Model):
	camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
	unit = models.ForeignKey(ClusterUnit, on_delete=models.CASCADE)
	processing_config = models.JSONField()

class EventType(models.Model):
	event_type = models.CharField(max_length=255)

	def __str__(self):
		return self.event_type

class Event(models.Model):
	processing_id = models.ForeignKey(Processing, on_delete=models.CASCADE)
	datestamp = models.DateTimeField()
	event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)

class DetectedObjectType(models.Model):
	type = models.CharField(max_length=255)

	def __str__(self):
		return self.type

class ObjectsDetectionLog(models.Model):
	datestamp = models.DateTimeField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	type = models.ForeignKey(DetectedObjectType, on_delete=models.CASCADE)
	count = models.IntegerField(default=0)
	