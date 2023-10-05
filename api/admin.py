from django.contrib import admin
from .models import (
    Camera,
    ClusterUnit, 
    Processing, 
    DetectedObjectType, 
    ObjectsDetectionLog, 
    Location,
    )


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_name', 'camera_ip', 'camera_description', 'input_location', 'output_location')

@admin.register(ClusterUnit)
class ClusterUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit_name', 'unit_ip', 'unit_config')

@admin.register(Processing)
class ProcessingAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_camera_name', 'view_unit_name', 'processing_config')

    def view_camera_name(self, obj):
        return obj.camera.camera_name
    
    def view_unit_name(self, obj):
        return obj.unit.unit_name

    view_camera_name.short_description = 'camera'
    view_unit_name.short_description = 'unit'

@admin.register(DetectedObjectType)
class DetectedObjectTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')

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
admin.site.unregister(ClusterUnit)
admin.site.register(ClusterUnit, ClusterUnitAdmin)
admin.site.unregister(Processing)
admin.site.register(Processing, ProcessingAdmin)
admin.site.unregister(DetectedObjectType)
admin.site.register(DetectedObjectType, DetectedObjectTypeAdmin)
admin.site.unregister(ObjectsDetectionLog)
admin.site.register(ObjectsDetectionLog, ObjectsDetectionLogsAdmin)
admin.site.unregister(Location)
admin.site.register(Location, LocationsAdmin)
