import asyncio
from rest_framework import generics
from django.http import JsonResponse
from api.models import Camera, ObjectsDetectionLog, DetectedObjectType
from api.serializers import CameraSerializer, ObjectsDetectionLogSerializer
from .kafka_consumer import main
from django.shortcuts import render


class ObjectsDetectionLogList(generics.ListCreateAPIView):
    queryset = ObjectsDetectionLog.objects.all()
    serializer_class = ObjectsDetectionLogSerializer

    async def perform_create(self, serializer):
        # instance = serializer.save()
        # data = instance.processing_config
        # asyncio.create_task(main()) # дописать добавление таски
        print(1)

        asyncio.create_task(main())

def start_kafka_consumer(request):
    asyncio.create_task(main())
    print(1)
    return JsonResponse({
        "message": "Kafka consumer started",
    })