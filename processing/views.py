from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from kafka import KafkaProducer
import json
from .models import (
    Camera,
    ProcessEvent,
    Model,
    ProcessAction,
    ComputerVisionModule,
    Process
)
from .serializers import (
    ModelSerializer, 
    ComputerVisionModuleSerializer, 
    ProcessActionSerializer, 
    ProcessEventSerializer, 
    ProcessSerializer
)

class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

class ComputerVisionModuleViewSet(viewsets.ModelViewSet):
    queryset = ComputerVisionModule.objects.all()
    serializer_class = ComputerVisionModuleSerializer

class ProcessActionViewSet(viewsets.ModelViewSet):
    queryset = ProcessAction.objects.all()
    serializer_class = ProcessActionSerializer

class ProcessEventViewSet(viewsets.ModelViewSet):
    queryset = ProcessEvent.objects.all()
    serializer_class = ProcessEventSerializer

class ProcessingViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'msg': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'events': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'event_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'event_actions': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING)
                                ),
                                'parameters': openapi.Schema(type=openapi.TYPE_OBJECT)
                            }
                        )
                    ),
                    'parameters': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'cvmode': openapi.Schema(type=openapi.TYPE_STRING),
                            'ip': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                }
            )
        }
    ))

    def create(self, request):
        body = request.data
        events = body['msg']['events']
        process_events = []
        for event in events:
            event_name = event['event_name']
            event_name_id = ProcessEvent.objects.filter(
                event_name=event_name).first() 
            actions = []

            for a in event['event_actions']:
                actions.append(
                    ProcessAction.objects.filter(action_name=a).first()) 

            process_event = ProcessEvent.objects.create(
                event=event_name_id,
                parameters=event['parameters'])

            process_event.actions.set(actions)

            process_events.append(process_event)

        process = Process.objects.create(
            cv_module=ComputerVisionModule.objects.filter(cv_modules_name=body['msg']['parameters']['cvmode']).first(),
            camera=Camera.objects.filter(camera_ip=body['msg']['parameters']['ip']).first(),
        )

        process.result_url = f'10.61.36.17/stream_{process.id}'
        body['msg']['events'][0]['parameters']['path_server_stream'] = f'stream_{process.id}'

        process.process_events.set(process_events)

        producer = KafkaProducer(
            bootstrap_servers=['10.61.36.15:9092', '10.61.36.15:9093','10.61.36.15:9094'],
            value_serializer=lambda v: v.encode('utf-8')
        )

        producer.send('cv_cons', json.dumps(body))
        producer.flush()

        return Response({"status": "Success"})