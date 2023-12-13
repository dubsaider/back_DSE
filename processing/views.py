from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from kafka import KafkaProducer
import json
from .models import (
    Camera,
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

        process = Process.objects.create(
            cv_module_id_id=data['cv_module_id'],
            camera_id_id=data['camera_id'],
            result_url='http://10.61.36.15:8554/' + data['camera_id'] + '/' + data['cv_module_id']
        )

        events_data = data['events']
        for event_data in events_data:
            event_type = event_data['event_type']
            actions_data = event_data['actions']

            process_event = ProcessEvent.objects.create(event_type=event_type)
            
            for action_data in actions_data:
                action_type = action_data['action_type']
                parameters = action_data['parameters']
                
                process_action = ProcessAction.objects.create(
                    action_type=action_type,
                    parameters=parameters
                )
                
                process_event.actions.add(process_action)

            process.events.add(process_event)

        return Response({'message': 'Process created successfully'}, status=status.HTTP_201_CREATED)