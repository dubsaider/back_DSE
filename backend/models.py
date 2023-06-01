from django.db import models


class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    preset_id = models.ForeignKey('CameraPreset', on_delete=models.CASCADE)
    camera_group_id = models.ForeignKey(
        'CameraGroup', on_delete=models.CASCADE)
    geo_coords = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    config_camera = models.JSONField()


class CameraModule(models.Model):
    id = models.AutoField(primary_key=True)
    camera_id = models.ForeignKey('Camera', on_delete=models.CASCADE)
    module_config = models.JSONField()


class CameraPreset(models.Model):
    id = models.AutoField(primary_key=True)
    preset_config = models.JSONField()


class CameraGroup(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField()
    floor_plan = models.CharField(max_length=255)


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.IntegerField()


class User(models.Model):
    id = models.AutoField(primary_key=True)
    login = models.IntegerField()
    password = models.IntegerField()
    role_id = models.ForeignKey('Role', on_delete=models.CASCADE)
