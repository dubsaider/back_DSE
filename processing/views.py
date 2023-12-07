from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from kafka import KafkaProducer
import json
from .models import (
    Camera,
    ProcessEvent,
    Model,
    ComputerVisionModule,
    Process
)
from .serializers import (
    ModelSerializer, 
    ComputerVisionModuleSerializer, 
    ProcessEventSerializer, 
    ProcessSerializer
)

class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

class ComputerVisionModuleViewSet(viewsets.ModelViewSet):
    queryset = ComputerVisionModule.objects.all()
    serializer_class = ComputerVisionModuleSerializer

class ProcessEventViewSet(viewsets.ModelViewSet):
    queryset = ProcessEvent.objects.all()
    serializer_class = ProcessEventSerializer

class ProcessingViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    def create(self, request):
        data = request.data

        model_name = data['cvmode']
        # TODO Не нужно создавать новый model
        model = Model.objects.create(model_name=model_name)

        cv_modules_name = data['cvmode']
        cv_module = ComputerVisionModule.objects.create(cv_modules_name=cv_modules_name, cv_modules_description=cv_modules_description, model_type=model)
        events = data['events']

        for event in events:
            event_type = event['event_type']
            fps = event['parameters'].get('FPS')
            line_count = event['event_actions'].count('line_count') > 0
            zone_check = event['event_actions'].count('box_drawing') > 0
            host_rtp = event['parameters'].get('host_port_rtsp_server').split(':')[0]
            port_rtp = int(event['parameters'].get('host_port_rtsp_server').split(':')[1])
            size_buff = None
            logging = event['event_actions'].count('logging') > 0
            box_drawing = event['event_actions'].count('box_drawing') > 0
            FPS_check = None
            process_event = ProcessEvent.objects.create(event_type=event_type, fps=fps, line_count=line_count, zone_check=zone_check, host_rtp=host_rtp, port_rtp=port_rtp, size_buff=size_buff, logging=logging, box_drawing=box_drawing, FPS_check=FPS_check)

        camera_id = data['camera_id']
        result_url = None
        process = Process.objects.create(cv_module_id=cv_module, camera_id=camera_id, all_frames_event=process_event, any_object_event=None, any_object_few_minutes_event=None, result_url=result_url)

        return Response({'message': 'Processing created successfully', 'data': {
            'model': model,
            'cv_module': cv_module,
            'process_event': process_event,
            'process': process
        }})