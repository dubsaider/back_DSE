from rest_framework import serializers
from .models import (
    Camera, 
    Stream,
    Location,
    CameraGroup
)
from processing.serializers import ProcessSerializer
from back.settings import K8S_ADDRESS

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CameraSerializer(serializers.ModelSerializer):
    processing_options = ProcessSerializer(many=True, read_only=True)
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ('id', 'camera_name', 'camera_ip', 'camera_description', 'camera_lat', 'camera_lon', 'is_active', 'processing_options', 'stream_url')
    
    def get_stream_url(self, obj):
        try:
            stream = Stream.objects.get(camera_id=obj.id)
            if stream.k8s_pod_name and stream.k8s_pod_port:
                return f"http://{K8S_ADDRESS}:{stream.k8s_pod_port}/api/stream.m3u8?src=stream{obj.id}&mp4=flac"
        except Stream.DoesNotExist:
            pass
        return None

class CameraGroupSerializer(serializers.ModelSerializer):
    cameras = CameraSerializer(many=True, read_only=True)

    class Meta:
        model = CameraGroup
        fields = ('id', 'group_name', 'cameras')

class StreamSerializer(serializers.ModelSerializer):
    camera = CameraSerializer()
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Stream
        fields = ('id', 'camera', 'k8s_pod_name', 'k8s_pod_port', 'status', 'created_at', 'stream_url')

    def get_stream_url(self, obj):
        if obj.k8s_pod_name and obj.k8s_pod_port:
            return f"http://{K8S_ADDRESS}:{obj.k8s_pod_port}/api/stream.m3u8?src=stream{obj.id}&mp4=flac"
        return None