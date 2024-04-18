from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json
from kafka import KafkaProducer
import requests
from .models import (
    Camera,
    ActionType,
    EventType,
    ProcessAction,
    ProcessEvent,
    Model,
    ComputerVisionModule,
    Process
)
from .serializers import (
    ModelSerializer, 
    ComputerVisionModuleSerializer, 
    ProcessEventSerializer, 
    ProcessSerializer,
    EventTypeSerializer,
    ActionTypeSerializer,
)

from back.settings import KAFKA, MEDIA_MTX

class ActionTypeViewSet(viewsets.ModelViewSet):
    queryset = ActionType.objects.all()
    serializer_class = ActionTypeSerializer
    http_method_names = ['get']

class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    http_method_names = ['get']

class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    http_method_names = ['get']

class ComputerVisionModuleViewSet(viewsets.ModelViewSet):
    queryset = ComputerVisionModule.objects.all()
    serializer_class = ComputerVisionModuleSerializer
    http_method_names = ['get']

class ProcessEventViewSet(viewsets.ModelViewSet):
    queryset = ProcessEvent.objects.all()
    serializer_class = ProcessEventSerializer

class ProcessingViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['camera__id']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            name='search',
            in_=openapi.IN_QUERY,
            description='Filter by camera ID',
            type=openapi.TYPE_STRING,
            required=False
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request):
        data = request.data
        cv_module_id = data['cv_module_id']
        camera_id = data['camera_id']
        process = Process.objects.create(
            cv_module_id=cv_module_id,
            camera_id=camera_id,
            result_url=f'http://{MEDIA_MTX}:8888/processing_{camera_id}/{cv_module_id}/stream.m3u8' 
        )
        events_data = data['events']
        for event_data in events_data:
            try:
                event_type = EventType.objects.get(id=event_data['event_type_id'])
            except ObjectDoesNotExist:
                return Response({'error': 'EventType not found'}, status=status.HTTP_400_BAD_REQUEST)

            process_event = ProcessEvent.objects.create(event_type=event_type)

            actions_data = event_data['actions']
            for action_data in actions_data:
                try:
                    action_type = ActionType.objects.get(id=action_data['action_type_id'])
                except ObjectDoesNotExist:
                    return Response({'error': 'ActionType not found'}, status=status.HTTP_400_BAD_REQUEST)

                process_action = ProcessAction.objects.create(
                    action_type=action_type,
                    parameters=action_data['parameters']
                )

                process_event.actions.add(process_action)

            process.events.add(process_event)

        cvmode = ComputerVisionModule.objects.filter(pk=data['cv_module_id']).first()
        camera = Camera.objects.filter(pk=data['camera_id']).first()
        print(cvmode, camera)
        kafka_msg = {
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
            "events": get_events(events_data)
          }
        }
        producer = KafkaProducer(bootstrap_servers=KAFKA,
                            value_serializer=lambda m: json.dumps(m).encode('utf-8')) 
        producer.send('cv_cons', kafka_msg)

        producer.flush()
        # json_data = json.dumps(data)

        # response = requests.post('http://10.61.36.18:4949/config', json=json_data)
        
        # if response.status_code == 200:
        return Response({'message': 'Process created successfully'}, status=status.HTTP_201_CREATED)
        # else:
        #     return Response({'error': 'Failed to send data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def get_events(events_data):
    event_list = []
    for event_data in events_data:
        try:
            event_type = EventType.objects.get(id=event_data['event_type_id'])
        except ObjectDoesNotExist:
            return Response({'error': 'EventType not found'}, status=status.HTTP_400_BAD_REQUEST)

        actions_data = event_data['actions']
        for action_data in actions_data:
            try:
                action_type = ActionType.objects.get(id=action_data['action_type_id'])
            except ObjectDoesNotExist:
                return Response({'error': 'ActionType not found'}, status=status.HTTP_400_BAD_REQUEST)

            events = {"event_name": event_type.name, "event_actions": action_type.name, "parameters": action_data['parameters']}
            event_list.append(events)

    return event_list


        