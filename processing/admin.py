from django.contrib import admin
from .models import Model, ComputerVisionModule, ProcessAction, ProcessEvent, Process, ActionType, EventType
from camera_manager.models import Camera
from kafka import KafkaProducer
import json

from back.settings import KAFKA, RTSP_SERVER

admin.site.register(EventType)

@admin.register(ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'parameters')

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'model_description')

@admin.register(ComputerVisionModule)
class ComputerVisionModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'cv_modules_name', 'cv_modules_description', 'model_type')

@admin.register(ProcessAction)
class ProcessActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_type', 'parameters')

@admin.register(ProcessEvent)
class ProcessEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_type', 'actions')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'cv_module_id', 'camera_id')
    
    def save_model(self, request, obj, form, change):
        producer = KafkaProducer(bootstrap_servers=KAFKA,
                                 value_serializer=lambda m: json.dumps(m).encode('utf-8')) 
        
        cvmode = ComputerVisionModule.objects.filter(pk=data['cv_module_id']).first()
        camera = Camera.objects.filter(pk=data['camera_id']).first()

        data = {
          "type": "create_process",
          "msg": {
            "parameters": {
              "cvmode": f"{cvmode.cv_modules_name}",
              "channel": 1,
              "port": 554,
              "ip": f"{camera.camera_ip}",
              "login": "", #TODO fix auth
              "password": "",
              "scene_number": 1
            },
            "events": [
              {
                  "event_name": "all_frames",
                  "event_actions": [
                    "box_drawing", "record", "rtsp_server_stream", "logging"
                  ],
                  "parameters": {
                    "FPS": 30,
                    "timer": 600,
                    "host_port_rtsp_server": RTSP_SERVER,
                    "path_server_stream": f"{data['camera_id']}/{data['cv_module_id']}"
                  }
                }
            ]
          }
        }

        json_data = json.dumps(data)

        producer.send('cv_cons', json_data)

        producer.flush()

        super().save_model(request, obj, form, change)
