from django.db import models
from camera_manager.models import Camera
from django.contrib.postgres.fields import ArrayField

class Model(models.Model):
	model_name = models.CharField(max_length=255)
	model_description = models.CharField(max_length=255, null=True)
	def __str__(self):
	    return self.model_name

class ComputerVisionModule(models.Model):
	cv_modules_name = models.CharField(max_length=255)
	cv_modules_description = models.CharField(max_length=255, null=True)
	model_type = models.ForeignKey(Model, on_delete=models.CASCADE, null=True, default=None)
	def __str__(self):
	    return self.cv_modules_name

class ActionType(models.Model):
  name = models.CharField(max_length=255)
  description = models.CharField(max_length=255, null=True, default=None)
  parameters = ArrayField(models.CharField(max_length=200), default=list)
  
  def __str__(self):
      return self.name

class ProcessAction(models.Model):
    action_type = models.ForeignKey(ActionType, on_delete=models.CASCADE)
    parameters = models.JSONField(null=True, default=None)
	
    def __str__(self):
        return f'{self.action_type} {self.parameters}'

class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, default=None)
    
    def __str__(self):
        return self.name


class ProcessEvent(models.Model):
	event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
	actions = models.ManyToManyField(ProcessAction)

	def __str__(self):
	    return f'{self.event_type} {[action for action in self.actions.all()]}'

class Process(models.Model):
	cv_module = models.ForeignKey(ComputerVisionModule, on_delete=models.CASCADE)
	camera = models.ForeignKey(Camera, related_name='processing_options', on_delete=models.CASCADE)
	events = models.ManyToManyField(ProcessEvent)
	
	def __str__(self):
	    return f"{self.camera.camera_name} - {self.cv_module.cv_modules_name}"