from django.contrib import admin
from .models import (
    Incident,
    IncidentType,
    CameraStat,
    ZoneStat
)

admin.site.register(IncidentType)
admin.site.register(CameraStat)
admin.site.register(ZoneStat)

@admin.register(Incident)
class ProcessActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera', 'start_timestamp', 'end_timestamp', 'incident_type', 'link', 'status', 'operator', 'is_system')
