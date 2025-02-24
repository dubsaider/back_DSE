from django.contrib import admin
from .models import (
    Camera,
    Stream,
    Location,
    CameraGroup,
)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_name', 'camera_ip', 'is_active', 'camera_description', 'camera_lon', 'camera_lat')

@admin.register(Location)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'location')

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'k8s_pod_name', 'k8s_pod_port', 'status', 'created_at', 'camera')

admin.site.unregister(Camera)
admin.site.register(Camera, CameraAdmin)
admin.site.unregister(Stream)
admin.site.register(Stream, StreamAdmin)
admin.site.unregister(Location)
admin.site.register(Location, LocationsAdmin)
admin.site.register(CameraGroup)

