from django.contrib import admin
from .models import (
    Camera,
    DetectedObjectType, 
    ObjectsDetectionLog, 
    Location,
    GroupType,
    CameraGroup,
    CameraToGroup,
    )


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_name', 'camera_ip', 'camera_description', 'input_location', 'output_location', 'camera_lon', 'camera_lat')

@admin.register(DetectedObjectType)
class DetectedObjectTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'description')

@admin.register(ObjectsDetectionLog)
class ObjectsDetectionLogsAdmin(admin.ModelAdmin):
    list_display = ('id', 'datestamp', 'view_location_name', 'view_type_name', 'count')

    def view_location_name(self, obj):
        return obj.location.location
    
    def view_type_name(self, obj):
        return obj.type.type

    view_location_name.short_description = 'location'
    view_type_name.short_description = 'type'

@admin.register(Location)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'location')



admin.site.unregister(Camera)
admin.site.register(Camera, CameraAdmin)
admin.site.unregister(DetectedObjectType)
admin.site.register(DetectedObjectType, DetectedObjectTypeAdmin)
admin.site.unregister(ObjectsDetectionLog)
admin.site.register(ObjectsDetectionLog, ObjectsDetectionLogsAdmin)
admin.site.unregister(Location)
admin.site.register(Location, LocationsAdmin)
admin.site.register(GroupType)
admin.site.register(CameraGroup)
admin.site.register(CameraToGroup)