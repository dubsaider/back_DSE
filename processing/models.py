from django.db import models
from api.models import Camera


class Model(models.Model):
	model_name = models.CharField(max_length=255)
	model_description = models.CharField(max_length=255, null=True)

class ComputerVisionModule(models.Model):
	cv_modules_name = models.CharField(max_length=255)
	cv_modules_description = models.CharField(max_length=255, null=True)
	model_type = models.ForeignKey(Model, on_delete=models.CASCADE, null=True, default=None)

class ProcessAction(models.Model):
    ACTION_CHOICES = (
        ('FPS', 'FPS'),
        ('logging', 'Logging'),
        ('line_count', 'Line Count'),
        ('zone_check', 'Zone Check'),
        ('rtp_stream', 'RTP Stream'),
        ('box_drawing', 'Box Drawing'),
        ('buffer_stream', 'Stream Buffer'),
        ('FPS_check', 'FPS Check'),
    )
	
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    fps = models.IntegerField(blank=True, null=True)
    line_count = models.JSONField(blank=True, null=True)
    zone_check = models.JSONField(blank=True, null=True)
    host_rtp = models.CharField(max_length=100, blank=True, null=True)
    port_rtp = models.IntegerField(blank=True, null=True)
    size_buff = models.IntegerField(blank=True, null=True)

class ProcessEvent(models.Model):
	ACTION_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )
	event_type = models.CharField(choices=ACTION_CHOICES)
	actions = models.ManyToManyField(ProcessAction)

class Process(models.Model):
	cv_module_id = models.ForeignKey(ComputerVisionModule, on_delete=models.CASCADE)
	camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)
	process_events = models.ManyToManyField(ProcessEvent)
	result_url = models.URLField(null=True, default=None)