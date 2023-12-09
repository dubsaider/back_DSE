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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)