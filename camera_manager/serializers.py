from rest_framework import serializers
from django.conf import settings
from .models import (
    Camera, 
    Location,
    GroupType,
    CameraGroup,
    CameraToGroup
)
import base64
import os


class CameraSerializer(serializers.ModelSerializer):
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ('id', 'camera_name', 'camera_ip', 'input_location', 'output_location', 'camera_description', 'camera_lon', 'camera_lat', 'is_active', 'preview')

    def get_preview(self, obj):
        image_path = f'cameras/camera_{obj.pk}/preview.jpg'
        if not obj.is_active or not os.path.exists(image_path):
            return
        # return f'{settings.MEDIA_URL}cameras/camera_{obj.pk}/preview.jpg'
        
        with open(image_path, 'rb') as img:
            image_str = base64.b64encode(img.read()).decode()
        return image_str      

class LocationSerializer(serializers.ModelSerializer):
     class Meta:
        model = Location
        fields = '__all__'

class GroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupType
        fields = ('type_name',)

class CameraGroupSerializer(serializers.ModelSerializer):
    group_type = GroupTypeSerializer()
    cameras = serializers.SerializerMethodField()

    def get_cameras(self, obj):
        camera_to_group = CameraToGroup.objects.filter(group_id=obj)
        cameras = [camera.camera_id for camera in camera_to_group]
        return CameraSerializer(cameras, many=True).data

    class Meta:
        model = CameraGroup
        fields = ('id', 'group_name', 'group_type', 'cameras')

class CameraToGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraToGroup
        fields = '__all__'