from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from .models import (
            DetectedObjectType,
            ObjectsDetectionLog,
        )
from .serializers import (
        ObjectsDetectionLogSerializer,
        DetectedObjectTypeSerializer,
    )
from rest_framework.permissions import (
        IsAuthenticated,
        IsAuthenticatedOrReadOnly
    )



class DetectedObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = DetectedObjectType.objects.all()
    serializer_class = DetectedObjectTypeSerializer
    http_method_names = ['get']

class ObjectsDetectionLogViewSet(viewsets.ViewSet):
    serializer_class = ObjectsDetectionLogSerializer
    http_method_names = ['get']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('start_datestamp', openapi.IN_QUERY, description="Start datestamp", type=openapi.TYPE_STRING),
        openapi.Parameter('end_datestamp', openapi.IN_QUERY, description="End datestamp", type=openapi.TYPE_STRING),
        openapi.Parameter('location', openapi.IN_QUERY, description="Location", type=openapi.TYPE_STRING),
        openapi.Parameter('type', openapi.IN_QUERY, description="Detection type", type=openapi.TYPE_STRING),
    ])
    def list(self, request):
        queryset = ObjectsDetectionLog.objects.all()

        start_datestamp = self.request.query_params.get('start_datestamp', None)
        end_datestamp = self.request.query_params.get('end_datestamp', None)
        location = self.request.query_params.get('location', None)
        detection_type = self.request.query_params.get('type', None)

        if start_datestamp:
            start_datestamp = datetime.strptime(start_datestamp, "%Y-%m-%dT%H:%M:%S")
            queryset = queryset.filter(datestamp__gte=start_datestamp)

        if end_datestamp:
            end_datestamp = datetime.strptime(end_datestamp, "%Y-%m-%dT%H:%M:%S")
            queryset = queryset.filter(datestamp__lte=end_datestamp)

        if location:
            if location.isnumeric():
                queryset = queryset.filter(location__pk=location)
            else:
                queryset = queryset.filter(location__location=location)

        if detection_type:
            queryset = queryset.filter(type__type=detection_type)

        serializer = ObjectsDetectionLogSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = ObjectsDetectionLog.objects.all()
        object_detection_log = get_object_or_404(queryset, pk=pk)
        serializer = ObjectsDetectionLogSerializer(object_detection_log)
        return Response(serializer.data)
