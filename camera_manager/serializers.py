from rest_framework import serializers
from .models import (
    Camera, 
    Location,
    GroupType,
    CameraGroup,
    CameraToGroup
)
from processing.serializers import ProcessSerializer


class CameraSerializer(serializers.ModelSerializer):
    raw_livestream = serializers.SerializerMethodField()
    processing_options = ProcessSerializer(many=True, read_only=True)

    class Meta:
        model = Camera
        fields = ('id', 'camera_name', 'camera_ip', 'input_location', 'output_location', 'camera_description', 'camera_lon', 'camera_lat', 'is_active', 'raw_livestream', 'processing_options')
    
    def get_raw_livestream(self, obj):
        if obj.is_active:
            login = 'admin'
            password = 'bvrn2022'
            return f'rtsp://{login}:{password}@{obj.camera_ip}:554/ISAPI/Streaming/Channels/101'
        return None
	
    def get_processed_livestream(self, obj):
        processing_options = obj.processing_options.all()
        return [option for option in processing_options]

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