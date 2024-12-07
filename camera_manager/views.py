from django.http import HttpResponseNotFound
from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import (
    Camera,
    Stream,
    Location,
    CameraGroup,
)
from .serializers import (
    CameraSerializer,
    StreamSerializer,
    LocationSerializer,
    CameraGroupSerializer,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from onvif import ONVIFCamera
import logging

logger = logging.getLogger(__name__)

class CameraViewSet(viewsets.ModelViewSet):
    serializer_class = CameraSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get_queryset(self):
        return Camera.objects.all()
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('groups', openapi.IN_QUERY, description="Filter cameras by group", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
    ])
    def list(self, request):
        queryset = self.get_queryset()
        groups = self.request.query_params.get('groups', None)
        if groups is not None:
            groups = groups.split(',')
            queryset = queryset.filter(camera_groups__in=groups)
        serializer = CameraSerializer(queryset, many=True)
        return Response(serializer.data)
    
class StreamViewSet(viewsets.ModelViewSet):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post']

class CameraGroupViewSet(viewsets.ModelViewSet):
    queryset = CameraGroup.objects.all()
    serializer_class = CameraGroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('group_name', openapi.IN_QUERY, description="Name of the group", type=openapi.TYPE_STRING),
        openapi.Parameter('cameras', openapi.IN_QUERY, description="IDs of cameras to add to the group", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
    ])
    def create(self, request):
        cameras = self.request.query_params.get('cameras', None)
        group_name = self.request.query_params.get('group_name', None)

        if group_name is None:
            return HttpResponseNotFound()
        
        group = CameraGroup.objects.create(
            group_name=group_name,
        )

        if cameras is not None:
            cameras = cameras.split(',')
            for camera_id in cameras:
                camera_obj = Camera.objects.filter(pk=camera_id).first()
                if camera_obj is not None:
                    group.cameras.add(camera_obj)

        return Response({"status": "success"})

def prepare_camera(mycam):
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
        openapi.Parameter('camera_id', openapi.IN_QUERY, description="ID of controlled camera", type=openapi.TYPE_INTEGER),
        openapi.Parameter('zoom_in', openapi.IN_QUERY, description="If True - camera will zoom in. It will zoom out otherwise", type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('speed', openapi.IN_QUERY, description="ms", type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
    ])
    def list(self, request):
        camera_id = request.query_params.get('camera_id')
        zoom_in = request.query_params.get('zoom_in') == 'true'
        speed = request.query_params.get('speed')
        speed = float(speed) if speed else 0.1
        camera = Camera.objects.get(id=camera_id)
    
        mycam = ONVIFCamera(camera.camera_ip, 80, '', '') #TODO fix auth
 
        moverequest = prepare_camera(mycam)
        
        moverequest.Translation.PanTilt.x = 0
        moverequest.Translation.PanTilt.y = 0
        moverequest.Translation.Zoom = 0
        if zoom_in:
            moverequest.Translation.Zoom = speed
        else:
            moverequest.Translation.Zoom = -speed
        
        mycam.ptz.RelativeMove(moverequest)
        return Response({'message': 'Camera zoom adjusted'})

class HikvisionCameraPositionViewSet(viewsets.ViewSet):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('camera_id', openapi.IN_QUERY, description="ID of controlled camera", type=openapi.TYPE_INTEGER),
        openapi.Parameter('direction', openapi.IN_QUERY, description="LEFT, RIGHT, UP, DOWN", type=openapi.TYPE_STRING),
        openapi.Parameter('speed', openapi.IN_QUERY, description="ms", type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
    ])
    def list(self, request):
        camera_id = request.query_params.get('camera_id')
        direction = request.query_params.get('direction')
        speed = request.query_params.get('speed')
        if not camera_id or not direction:
            return Response({'detail': 'camera_id and direction are required'}, status=400)
        speed = float(speed) if speed else 0.005

        mycam = Camera.objects.get(id=camera_id)
        mycam = ONVIFCamera(mycam.camera_ip, 80, '', '')

        moverequest = prepare_camera(mycam)

        moverequest.Translation.Zoom = 0
        moverequest.Translation.PanTilt.x = 0
        moverequest.Translation.PanTilt.y = 0
        if direction == "RIGHT":
            moverequest.Translation.PanTilt.x = speed
        elif direction == "LEFT":
            moverequest.Translation.PanTilt.x = -speed
        elif direction == "UP":
            moverequest.Translation.PanTilt.y = speed
        elif direction == "DOWN":
            moverequest.Translation.PanTilt.y = -speed
        
        mycam.ptz.RelativeMove(moverequest)

        return Response({'message': 'Camera moved'})