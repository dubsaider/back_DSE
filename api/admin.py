from django.contrib import admin
from .models import (
    Incident,
    IncidentType,
    CameraStat,
    ZoneStat
)


admin.site.register(Incident)
admin.site.register(IncidentType)
admin.site.register(CameraStat)
admin.site.register(ZoneStat)
