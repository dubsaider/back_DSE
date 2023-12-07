from django.contrib import admin
from .models import Model, ComputerVisionModule, ProcessEvent, Process


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_description')

@admin.register(ComputerVisionModule)
class ComputerVisionModuleAdmin(admin.ModelAdmin):
    list_display = ('cv_modules_name', 'cv_modules_description', 'model_type')

@admin.register(ProcessEvent)
class ProcessEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'fps', 'line_count', 'zone_check', 'host_rtp', 'port_rtp', 'size_buff', 'logging', 'box_drawing', 'FPS_check')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('cv_module_id', 'camera_id', 'all_frames_event', 'any_object_event', 'any_object_few_minutes_event', 'result_url')
