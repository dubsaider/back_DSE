from rest_framework import serializers
from .models import (
    Camera, 
    Stream,
    Location,
    CameraGroup
)
from processing.serializers import ProcessSerializer
from back.settings import K8S_ADDRESS

class BaseSerializer(serializers.ModelSerializer):
    def get_hls_url(self, obj):
        try:
            stream = Stream.objects.get(camera_id=obj.id)
            if stream.k8s_pod_name and stream.k8s_pod_port:
                return f"http://{K8S_ADDRESS}:6443/cameras/go2rtc-{stream.camera_id}/api/ws?src=camera-{stream.camera_id}"
        except Stream.DoesNotExist:
            pass
        return None

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CameraSerializer(BaseSerializer):
    processing_options = ProcessSerializer(many=True, read_only=True)
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ('id', 'camera_name', 'camera_ip', 'camera_description', 'camera_lat', 'camera_lon', 'is_active', 'processing_options', 'stream_url')
    
    def get_stream_url(self, obj):
        return self.get_hls_url(obj)

class CameraGroupSerializer(serializers.ModelSerializer):
    cameras = CameraSerializer(many=True, read_only=True)

    class Meta:
        model = CameraGroup
        fields = ('id', 'group_name', 'cameras')

class StreamSerializer(BaseSerializer):
    camera = CameraSerializer()
    stream_url = serializers.SerializerMethodField()

    class Meta:
        model = Stream
        fields = ('id', 'camera', 'k8s_pod_name', 'k8s_pod_port', 'status', 'created_at', 'stream_url')

    def get_stream_url(self, obj):
        return self.get_hls_url(obj.camera)