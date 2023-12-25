from django.contrib import admin
from .models import Model, ComputerVisionModule, ProcessAction, ProcessEvent, Process
from camera_manager.models import Camera
from kafka import KafkaProducer
import json


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
    list_display = ('id', 'cv_module_id', 'camera_id', 'result_url')
    
    def save_model(self, request, obj, form, change):
        obj.result_url = f'http://10.61.36.15:8888/processing_{obj.camera_id.id}/{obj.cv_module_id.id}'

        producer = KafkaProducer(bootstrap_servers=['10.61.36.15:9092', '10.61.36.15:9093', '10.61.36.15:9094'],
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
              "login": "admin",
              "password": "bvrn2022",
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
                    "host_port_rtsp_server": "10.61.36.17:8554",
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
