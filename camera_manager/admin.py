from django.contrib import admin
from .models import (
    Camera,
    Location,
    GroupType,
    CameraGroup,
    CameraToGroup,
    Stream,
)
from back.settings import K8S_ADDRESS


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_name', 'camera_ip', 'is_active', 'camera_description', 'camera_lon', 'camera_lat')

@admin.register(Location)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'location')

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'k8s_pod_name', 'k8s_pod_port', 'status', 'created_at', 'camera', 'stream_url')

    def stream_url(self, obj):
        if obj.k8s_pod_name and obj.k8s_pod_port:
            return f"http://{K8S_ADDRESS}:{obj.k8s_pod_port}/convert_to_hls/streams/{obj.camera.id}/stream.m3u8"
        return None

    stream_url.short_description = 'Stream URL'

admin.site.unregister(Camera)
admin.site.register(Camera, CameraAdmin)
admin.site.unregister(Stream)
admin.site.register(Stream, StreamAdmin)
admin.site.unregister(Location)
admin.site.register(Location, LocationsAdmin)
admin.site.register(GroupType)
admin.site.register(CameraGroup)
admin.site.register(CameraToGroup)

