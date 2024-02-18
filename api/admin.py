from django.contrib import admin
from .models import (
    DetectedObjectType, 
    ObjectsDetectionLog,
    Incident,
    IncidentType,
    CameraStats,
    ZoneStats
)


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



admin.site.unregister(DetectedObjectType)
admin.site.register(DetectedObjectType, DetectedObjectTypeAdmin)
admin.site.unregister(ObjectsDetectionLog)
admin.site.register(ObjectsDetectionLog, ObjectsDetectionLogsAdmin)
admin.site.register(Incident)
admin.site.register(IncidentType)
admin.site.register(CameraStats)
admin.site.register(ZoneStats)
