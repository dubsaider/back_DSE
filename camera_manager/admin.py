from django.contrib import admin
from .models import (
    Camera,
    Location,
    GroupType,
    CameraGroup,
    CameraToGroup,
)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_name', 'camera_ip', 'camera_description', 'input_location', 'output_location', 'camera_lon', 'camera_lat')

@admin.register(Location)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'location')

admin.site.unregister(Camera)
admin.site.register(Camera, CameraAdmin)
admin.site.unregister(Location)
admin.site.register(Location, LocationsAdmin)
admin.site.register(GroupType)
admin.site.register(CameraGroup)
admin.site.register(CameraToGroup)
