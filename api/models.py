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
	camera_description = models.CharField(max_length=255, null=True, default='null')

	def __str__(self):
		return self.camera_name
	
class ClusterUnit(models.Model):
	unit_name = models.CharField(max_length=255)
	unit_ip = models.CharField(max_length=15)
	unit_config = models.JSONField(null=True, default=None)

	def __str__(self):
		return self.unit_name

class Model(models.Model):
	model_name = models.CharField(max_length=255)
	model_description = models.CharField(max_length=255, null=True)

class Processing(models.Model):
	camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
	unit = models.ForeignKey(ClusterUnit, on_delete=models.CASCADE)
	processing_config = models.JSONField(default=None, null=True)
	result_url = models.URLField(null=True, default=None)

class ComputerVisionModule(models.Model):
	cv_modules_name = models.CharField(max_length=255)
	cv_modules_description = models.CharField(max_length=255, null=True)
	model_type = models.ForeignKey(Model, on_delete=models.CASCADE, null=True, default=None)

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

class EventType(models.Model):
	event_name = models.CharField(max_length=255)
	event_description = models.CharField(max_length=255, null=True)
	parameters = models.JSONField(null=True, default=None)

	def __str__(self):
		return self.event_name


class Event(models.Model):
	processing_id = models.ForeignKey(Processing, on_delete=models.CASCADE)
	datestamp = models.DateTimeField()
	event_name = models.ForeignKey(EventType, on_delete=models.CASCADE)
	video_url = models.URLField(null=True, default=None)


class Action(models.Model):
	action_name = models.CharField(max_length=255)
	action_description = models.CharField(max_length=255, null=True)
	parameters = models.JSONField(null=True, default=None)

	def __str__(self):
		return self.action_name


class ProcessEvent(models.Model):
	event = models.ForeignKey(EventType, on_delete=models.CASCADE)
	actions = models.ManyToManyField(Action)
	parameters = models.JSONField(null=True, default=None)

class Process(models.Model):
	cv_module = models.ForeignKey(ComputerVisionModule, on_delete=models.CASCADE)
	camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
	process_events = models.ManyToManyField(ProcessEvent)


class GroupType(models.Model):
	type_name = models.CharField(max_length=255)
	
	def __str__(self):
		return self.type_name

class CameraGroup(models.Model):
	group_name = models.CharField(max_length=255)
	group_type = models.ForeignKey(GroupType, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.group_name

class CameraToGroup(models.Model):
	group_id = models.ForeignKey(CameraGroup, on_delete=models.CASCADE)
	camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)
	