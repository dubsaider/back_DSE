from django.db import models
from api.models import Camera


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

class ProcessAction(models.Model):
    ACTION_TYPE_CHOICES = (
        ('record', 'Record'),
        ('logging', 'Logging'),
        ('line_count', 'Line Count'),
        ('zone_check', 'Zone Check'),
        ('rtp_stream', 'RTP Stream'),
        ('box_drawing', 'Box Drawing'),
        ('buffer_stream', 'Stream Buffer'),
		('rtsp_server_stream', 'RTSP Stream Server'),
        ('FPS_check', 'FPS Check'),
    )
    action_type = models.CharField(choices=ACTION_TYPE_CHOICES)
    parameters = models.JSONField(null=True, default=None)
	
    def __str__(self):
        return f'{self.action_type} {self.parameters}'

class ProcessEvent(models.Model):
	EVENT_TYPE_CHOICES = (
        ('all_frames', 'All frames'),
        ('check_any_object', 'Check any object'),
        ('check_any_object_few_minutes', 'Check any object few minutes'),
    )
	event_type = models.CharField(choices=EVENT_TYPE_CHOICES, null=False)
	actions = models.ManyToManyField(ProcessAction)

	def __str__(self):
	    return f'{self.event_type} {[action for action in self.actions.all()]}'

class Process(models.Model):
	cv_module_id = models.ForeignKey(ComputerVisionModule, on_delete=models.CASCADE)
	camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)
	events = models.ManyToManyField(ProcessEvent)
	result_url = models.URLField(null=True, blank=True)
	
	def __str__(self):
	    return f"{self.camera_id.camera_name} - {self.cv_module_id.cv_modules_name}"