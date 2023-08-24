from django.shortcuts import render
from rest_framework import generics
from .models import Camera, ClusterUnit, Processing, ObjectsDetectionLogs
from .serializers import CameraSerializer, ClusterUnitSerializer, ProcessingSerializer, ObjectsDetectionLogsSerializer
from django.http import HttpResponse
from datetime import datetime


class CameraList(generics.ListCreateAPIView):
    quaryset = Camera.objects.all()
    serializer_class = CameraSerializer

class ClusterUnitList(generics.ListCreateAPIView):
    queryset = ClusterUnit.objects.all()
    serializer_class = ClusterUnitSerializer

class ProcessingList(generics.ListCreateAPIView):
    queryset = Processing.objects.all()
    serializer_class = ProcessingSerializer

class ObjectsDetectionLogsList(generics.ListCreateAPIView):
    serializer_class = ObjectsDetectionLogsSerializer

    def get_queryset(self):
        queryset = ObjectsDetectionLogs.objects.all()

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
            queryset = queryset.filter(location__location=location)
        

        if detection_type:
            queryset = queryset.filter(type__type=detection_type)

        return queryset

def test(requset):
    st = "<h4>"  + "</h4>"
    return HttpResponse(ObjectsDetectionLogs.objects.first().__str__)