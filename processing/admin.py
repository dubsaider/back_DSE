from django.contrib import admin
from .models import Model, ComputerVisionModule, ProcessAction, ProcessEvent, Process


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_description')

@admin.register(ComputerVisionModule)
class ComputerVisionModuleAdmin(admin.ModelAdmin):
    list_display = ('cv_modules_name', 'cv_modules_description', 'model_type')

@admin.register(ProcessAction)
class ProcessActionAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'parameters')

@admin.register(ProcessEvent)
class ProcessEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'actions')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('cv_module_id', 'camera_id', 'result_url')
    
    def save_model(self, request, obj, form, change):
        obj.result_url = f'http://10.61.36.15:8554/{obj.camera_id.id}/{obj.cv_module_id.id}'

        super().save_model(request, obj, form, change)
