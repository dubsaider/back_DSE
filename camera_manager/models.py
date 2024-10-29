from django.db import models	
from django.db.models import JSONField	

class Location(models.Model):
	location = models.CharField(max_length=255)
	coordinates = JSONField(default=list)

	def __str__(self):
		return self.location
	
class Camera(models.Model):
    camera_name = models.CharField(max_length=255)
    camera_ip = models.CharField(max_length=15)
    camera_description = models.CharField(max_length=255, null=True, default='null')
    camera_lat = models.FloatField(default=0.0)
    camera_lon = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.camera_name
	
class CameraTransition(models.Model):
    from_camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='transitions_from')
    to_camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='transitions_to')
    transition_description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Transition from {self.from_camera.camera_name} to {self.to_camera.camera_name}"
	
class Stream(models.Model):
	camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
	k8s_pod_name = models.CharField(max_length=255, null=True, blank=True)
	k8s_pod_port = models.CharField(max_length=5, null=True, blank=True) 
	status = models.CharField(max_length=50, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
	    return f"Stream for {self.camera.camera_name}"
	
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