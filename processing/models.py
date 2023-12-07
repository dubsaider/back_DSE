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


class ProcessEvent(models.Model):
	fps = models.IntegerField(blank=True, null=True)
	line_count = models.JSONField(blank=True, null=True)
	zone_check = models.JSONField(blank=True, null=True)
	host_rtp = models.CharField(max_length=100, blank=True, null=True)
	port_rtp = models.IntegerField(blank=True, null=True)
	size_buff = models.IntegerField(blank=True, null=True)
	logging = models.BooleanField(blank=True, null=True)
	box_drawing = models.BooleanField(blank=True, null=True)
	FPS_check = models.BooleanField(blank=True, null=True)
	
    # def __str__(self):
	# 	fields = []
    #     if self.fps is not None:
    #         fields.append(f"fps=self.fps")
    #     if self.line_count is not None:
    #         fields.append(f"line_count=self.line_count")
    #     if self.zone_check is not None:
    #         fields.append(f"zone_check=self.zone_check")
    #     if self.host_rtp is not None:
    #         fields.append(f"host_rtp=self.host_rtp")
    #     if self.port_rtp is not None:
    #         fields.append(f"port_rtp=self.port_rtp")
    #     if self.size_buff is not None:
    #         fields.append(f"size_buff=self.size_buff")
    #     if self.logging is not None:
    #         fields.append(f"logging=self.logging")
    #     if self.box_drawing is not None:
    #         fields.append(f"box_drawing=self.box_drawing")
    #     if self.FPS_check is not None:
    #         fields.append(f"FPS_check=self.FPS_check")

    #     return ", ".join(fields)
	
class Process(models.Model):
	cv_module_id = models.ForeignKey(ComputerVisionModule, on_delete=models.CASCADE)
	camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)
	all_frames_event = models.ForeignKey(ProcessEvent, on_delete=models.CASCADE, null=True, related_name='all_frames')
	any_object_event = models.ForeignKey(ProcessEvent, on_delete=models.CASCADE, null=True, related_name='any_object')
	any_object_few_minutes_event = models.ForeignKey(ProcessEvent, on_delete=models.CASCADE, null=True, related_name='any_object_few_minutes')
	result_url = models.URLField(null=True, default=None)
	
	def __str__(self):
	    return f"{self.camera_id.camera_name} - {self.cv_module_id.cv_modules_name}"