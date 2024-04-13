from django.shortcuts import render
import os
from pathlib import Path
import ffmpeg_streaming
from onvif import ONVIFCamera
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import (
            Camera, 
            Location,
            GroupType,
            CameraGroup,
            CameraToGroup,
        )
from .serializers import (
        CameraSerializer, 
        LocationSerializer,
        GroupTypeSerializer,
        CameraGroupSerializer,
        CameraToGroupSerializer,
    )
from rest_framework.permissions import (
        IsAuthenticated,
        IsAuthenticatedOrReadOnly
    )

class CameraViewSet(viewsets.ModelViewSet):
    serializer_class = CameraSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
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
    http_method_names = ['get', 'post']

class GroupTypeViewSet(viewsets.ModelViewSet):
    queryset = GroupType.objects.all()
    serializer_class = GroupTypeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get']

class CameraGroupViewSet(viewsets.ModelViewSet):
    queryset = CameraGroup.objects.all()
    serializer_class = CameraGroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get']

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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CameraToGroupSerializer

ACTIVE_STREAMS = {}

def start_stream(ip, hls_output_dir, pk):
    stream_output_dir = os.path.join(hls_output_dir, 'stream.m3u8')
    video = ffmpeg_streaming.input(f'rtsp://admin:bvrn2022@{ip}:554/ISAPI/Streaming/Channels/101', hls_time=5, preset='ultrafast')
    hls_stream = video.hls(ffmpeg_streaming.Formats.h264(), hls_list_size = 5)
    _720p = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(1280, 720), ffmpeg_streaming.Bitrate(2048 * 1024, 320 * 1024))
    hls_stream.representations(_720p)
    hls_stream.flags('delete_segments')
    if not os.path.isfile(stream_output_dir):
        hls_stream.output(f'cameras/camera_{pk}/stream.m3u8')
    return hls_stream

    
def get_camera_view(request=None, pk=None, filename='stream.m3u8'):
    
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


def prepeare_camera(mycam):
    ptz = mycam.create_ptz_service()

    media = mycam.create_media_service()

    media_profile = media.GetProfiles()[0]

    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    moverequest = ptz.create_type('RelativeMove')
    moverequest.ProfileToken = media_profile.token
    if moverequest.Translation is None:
        moverequest.Translation = ptz.GetStatus(
            {'ProfileToken': media_profile.token}).Position
        moverequest.Translation.PanTilt.space = ptz_configuration_options.Spaces.RelativePanTiltTranslationSpace[0].URI
        moverequest.Translation.Zoom.space = ptz_configuration_options.Spaces.RelativeZoomTranslationSpace[0].URI
        if moverequest.Speed is None:
            moverequest.Speed = ptz.GetStatus(
                {'ProfileToken': media_profile.token}).Position
    return moverequest
            

class HikvisionCameraZoomViewSet(viewsets.ViewSet):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('camera_id', openapi.IN_QUERY, description="id of controlled camera", type=openapi.TYPE_INTEGER),
        openapi.Parameter('zoom_in', openapi.IN_QUERY, description="if True - camera will zoom in. It will zoom out otherwise", type=openapi.TYPE_BOOLEAN),
    ])

    def create(self, request):
        camera_id = request.query_params['camera_id']
        zoom_in = request.query_params['zoom_in']

        camera = Camera.objects.get(id=camera_id)
    
        mycam = ONVIFCamera(camera.camera_ip, 80, 'admin', 'bvrn2022')
        moverequest = prepeare_camera(mycam=mycam)
        
        moverequest.Translation.PanTilt.x = 0
        moverequest.Translation.PanTilt.y = 0
        moverequest.Translation.Zoom = 0
        if zoom_in:
            moverequest.Translation.Zoom = 0.003
        else:
            moverequest.Translation.Zoom = -0.003
        
        mycam.ptz.RelativeMove(moverequest)
        return Response({'message': 'Camera zoomed in'})

class HikvisionCameraPositionViewSet(viewsets.ViewSet):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('camera_id', openapi.IN_QUERY, description="id of controlled camera", type=openapi.TYPE_INTEGER),
        openapi.Parameter('direction', openapi.IN_QUERY, description="LEFT, RIGHT, UP, DOWN", type=openapi.TYPE_STRING),
    ])

    def create(self, request):
        camera_id = request.query_params['camera_id']
        direction = request.query_params['direction']
        mycam = Camera.objects.get(id=camera_id)
    
        mycam = ONVIFCamera(mycam.camera_ip, 80, 'admin', 'bvrn2022')

        moverequest = prepeare_camera(mycam=mycam)

        moverequest.Translation.Zoom = 0
        moverequest.Translation.PanTilt.x = 0
        moverequest.Translation.PanTilt.y = 0
        if direction == "RIGHT":
            moverequest.Translation.PanTilt.x = 0.003
        elif direction == "LEFT":
            moverequest.Translation.PanTilt.x = -0.003
        elif direction == "UP":
            moverequest.Translation.PanTilt.y = 0.003
        elif direction == "DOWN":
            moverequest.Translation.PanTilt.y = -0.003
        
        mycam.ptz.RelativeMove(moverequest)

        return Response({'message': 'Camera moved'})
    