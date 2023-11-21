import os
from pathlib import Path
import ffmpeg_streaming
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.response import Response
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime, timedelta
from .models import (
            Camera, 
            ClusterUnit, 
            Processing,
            Location,
            DetectedObjectType,
            ObjectsDetectionLog,
            EventType,
            Action,
            Model,
            ComputerVisionModule,
            Event,
            ProcessEvent,
            Process,
        )
from .serializers import (
        CameraSerializer, 
        ClusterUnitSerializer, 
        ProcessingSerializer, 
        ObjectsDetectionLogSerializer,
        ProcessSerializer,
        LocationSerializer,
        EventTypeSerializer,
        ActionSerializer,
        ModelSerializer,
        ComputerVisionModuleSerializer,
        EventSerializer,
        DetectedObjectTypeSerializer
    )
import json
from rest_framework.decorators import api_view


class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

class ActionViewSet(viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer

class ModelsViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

class ComputerVisionModulesViewSet(viewsets.ModelViewSet):
    queryset = ComputerVisionModule.objects.all()
    serializer_class = ComputerVisionModuleSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class DetectedObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = DetectedObjectType.objects.all()
    serializer_class = DetectedObjectTypeSerializer

class CameraViewSet(viewsets.ModelViewSet):
    # quaryset = Camera.objects.all()
    serializer_class = CameraSerializer

    def get_queryset(self):
        return Camera.objects.all()

class ClusterUnitViewSet(viewsets.ModelViewSet):
    queryset = ClusterUnit.objects.all()
    serializer_class = ClusterUnitSerializer

class ProcessingViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class ObjectsDetectionLogViewSet(viewsets.ViewSet):
    serializer_class = ObjectsDetectionLogSerializer

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

@api_view(['POST'])
@csrf_exempt 
def process_handler(self):
    body_unicode = self.body.decode('utf-8')
    body = json.loads(body_unicode)  
    events = body['msg']['events']
    process_events = []
    for event in events:
        event_name = event['event_name']
        event_name_id = EventType.objects.filter(
            event_name=event_name).first() 
        actions = []

        for a in event['event_actions']:
            actions.append(
                Action.objects.filter(action_name=a).first()) 

        process_event = ProcessEvent.objects.create(
            event=event_name_id,
            parameters=event['parameters'])

        process_event.actions.set(actions)

        process_events.append(process_event)

    process = Process.objects.create(
        cv_module=ComputerVisionModule.objects.filter(cv_modules_name=body['msg']['parameters']['cvmode']).first(),
        camera=Camera.objects.filter(camera_ip=body['msg']['parameters']['ip']).first(),
    )

    process.process_events.set(process_events)

    return Response({"status": "success"})

def video_hls_view(request, filename):
    video_path = '/home/ubuntuser/back_DSE/vid/L.mp4'

    hls_output_dir = os.path.join(os.path.dirname(video_path), 'test')
    playlist_path = os.path.join(hls_output_dir, filename)

    with open(playlist_path, 'rb') as playlist_file:
        response = HttpResponse(playlist_file.read(), content_type='application/vnd.apple.mpegurl')
        return response


ACTIVE_STREAMS = {}

def start_stream(ip, hls_output_dir, pk):
    stream_output_dir = os.path.join(hls_output_dir, 'stream.m3u8')
    video = ffmpeg_streaming.input(f'rtsp://admin:bvrn2022@{ip}:554/ISAPI/Streaming/Channels/101')
    hls_stream = video.hls(ffmpeg_streaming.Formats.h264(), hls_list_size = 10)
    _720p = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(1280, 720), ffmpeg_streaming.Bitrate(2048 * 1024, 320 * 1024))
    hls_stream.representations(_720p)
    hls_stream.flags('delete_segments')
    if not os.path.isfile(stream_output_dir):
        hls_stream.output(f'cameras/camera_{pk}/stream.m3u8')
    return hls_stream

    
def get_camera_view(request, pk, filename):
    
    if not Camera.objects.filter(pk=pk).exists():
        return HttpResponseNotFound()
    

    camera_ip = Camera.objects.filter(pk=pk).first().camera_ip
    hls_output_dir = os.path.join(Path(__file__).resolve().parent.parent, 'cameras')
    hls_output_dir = os.path.join(hls_output_dir, f'camera_{pk}')

    if f'camera_{pk}' not in ACTIVE_STREAMS.keys():
        if not os.path.exists(hls_output_dir):
            os.makedirs(hls_output_dir)
        
        

        ACTIVE_STREAMS[f'camera_{pk}'] = start_stream(camera_ip, hls_output_dir, pk)

    playlist_path = os.path.join(hls_output_dir, filename)

    with open(playlist_path, 'rb') as playlist_file:
        response = HttpResponse(playlist_file.read(), content_type='application/vnd.apple.mpegurl')
        return response