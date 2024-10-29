from rest_framework import serializers
from .models import (
    Camera, 
    Stream,
    Location,
    GroupType,
    CameraGroup,
    CameraToGroup
)
from processing.serializers import ProcessSerializer
from back.settings import K8S_ADDRESS

class LocationSerializer(serializers.ModelSerializer):
     class Meta:
        model = Location
        fields = '__all__'

class CameraSerializer(serializers.ModelSerializer):
    processing_options = ProcessSerializer(many=True, read_only=True)

    class Meta:
        model = Camera
        fields = ('id', 'camera_name', 'camera_ip', 'camera_description', 'camera_lon', 'camera_lat', 'is_active', 'processing_options')
    

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

class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = '__all__'

    def get_stream_url(self, obj):
        if obj.k8s_pod_name and obj.k8s_pod_port:
            return f"http://{K8S_ADDRESS}:{obj.k8s_pod_port}/convert_to_hls/streams/{obj.camera.id}/stream.m3u8"
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['stream_url'] = self.get_stream_url(instance)
        return representation
