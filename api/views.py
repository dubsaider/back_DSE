import os
from pathlib import Path
import ffmpeg_streaming
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from .models import (
            Camera, 
            Location,
            DetectedObjectType,
            ObjectsDetectionLog,
            GroupType,
            CameraGroup,
            CameraToGroup,
        )
from .serializers import (
        CameraSerializer, 
        ObjectsDetectionLogSerializer,
        LocationSerializer,
        DetectedObjectTypeSerializer,
        GroupTypeSerializer,
        CameraGroupSerializer,
        CameraToGroupSerializer,
    )
from rest_framework.permissions import (
        IsAuthenticated,
        IsAuthenticatedOrReadOnly
    )



class DetectedObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = DetectedObjectType.objects.all()
    serializer_class = DetectedObjectTypeSerializer

class CameraViewSet(viewsets.ModelViewSet):
    serializer_class = CameraSerializer
    
    def get_queryset(self):
        return Camera.objects.all()
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('groups', openapi.IN_QUERY, description="Insert cameras into group", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
    ])
    def list(self, request):
        queryset = self.get_queryset()
        groups = self.request.query_params.get('groups', None)
        if groups is not None:
            groups = groups.split(',')
            queryset_filter = CameraToGroup.objects.filter(group_id__in=groups)
            queryset = queryset.filter(pk__in=queryset_filter.values('camera_id'))
        serializer = CameraSerializer(queryset, many=True)
        return Response(serializer.data)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

class GroupTypeViewSet(viewsets.ModelViewSet):
    queryset = GroupType.objects.all()
    serializer_class = GroupTypeSerializer

class CameraGroupViewSet(viewsets.ModelViewSet):
    queryset = CameraGroup.objects.all()
    serializer_class = CameraGroupSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('group_name', openapi.IN_QUERY, description="Insert cameras into group", type=openapi.TYPE_STRING),
        openapi.Parameter('group_type', openapi.IN_QUERY, description="Insert cameras into group", type=openapi.TYPE_INTEGER),
        openapi.Parameter('cameras', openapi.IN_QUERY, description="Insert cameras into group", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
    ])
    def create(self, request):
        cameras = self.request.query_params.get('cameras', None)
        group_name = self.request.query_params.get('group_name', None)
        group_type = self.request.query_params.get('group_type', None)

        if group_name is None or group_type is None:
            return HttpResponseNotFound()
        
        group = CameraGroup.objects.create(
            group_name=group_name,
            group_type=GroupType.objects.filter(pk=group_type).first()
        )

        if cameras is not None:
            cameras = cameras.split(',')
            for camera in cameras:
                camera_obj = Camera.objects.filter(pk=camera).first()
                if camera_obj is None:
                    continue
                CameraToGroup.objects.create(
                    group_id=group,
                    camera_id=camera_obj,
                )
        # TODO: Add normal response in "Denis`s style"
        return Response({"status": "success"})

class CameraToGroupViewSet(viewsets.ModelViewSet):
    queryset = CameraToGroup.objects.all()
    serializer_class = CameraToGroupSerializer

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