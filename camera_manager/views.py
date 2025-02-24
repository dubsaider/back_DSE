from django.http import HttpResponseNotFound
from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import Camera, Stream, Location, CameraGroup
from .serializers import CameraSerializer, StreamSerializer, LocationSerializer, CameraGroupSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from onvif import ONVIFCamera
import logging
from utils.k8s_utils import get_k8s_apis, get_secrets

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
    permission_classes = [IsAuthenticatedOrReadOnly]


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
        ungrouped_cameras = Camera.objects.filter(camera_groups__isnull=True)
        ungrouped_cameras_serializer = CameraSerializer(ungrouped_cameras, many=True)
        ungrouped_group = {
            "id": -1,
            "group_name": "Без группы",
            "cameras": ungrouped_cameras_serializer.data
        }
        response_data = serializer.data
        response_data.append(ungrouped_group)
        return Response(response_data)

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


class PTZController:
    def __init__(self, camera):
        self.camera = camera
        core_v1_api, _, _ = get_k8s_apis()
        secret_name = f"camera-secret-{camera.id}"
        secrets = get_secrets(core_v1_api, secret_name)
        if secrets is None:
            raise ValueError("Не удалось получить секреты для камеры")

        self.login, self.password = secrets
        try:
            self.mycam = ONVIFCamera(camera.camera_ip, 80, self.login, self.password)
            self.ptz = self.mycam.create_ptz_service()
            self.media = self.mycam.create_media_service()
            self.media_profile = self.media.GetProfiles()[0]
        except Exception as e:
            raise ValueError(f"Ошибка при создании ONVIFCamera: {e}") from e

    def prepare_move_request(self):
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)
        moverequest = self.ptz.create_type('RelativeMove')
        moverequest.ProfileToken = self.media_profile.token
        if moverequest.Translation is None:
            moverequest.Translation = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position
            moverequest.Translation.PanTilt.space = ptz_configuration_options.Spaces.RelativePanTiltTranslationSpace[0].URI
            moverequest.Translation.Zoom.space = ptz_configuration_options.Spaces.RelativeZoomTranslationSpace[0].URI
            if moverequest.Speed is None:
                moverequest.Speed = self.ptz.GetStatus(
                    {'ProfileToken': self.media_profile.token}).Position
        return moverequest

    def move_camera(self, direction, speed):
        moverequest = self.prepare_move_request()
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
        self.ptz.RelativeMove(moverequest)

    def zoom_camera(self, zoom_in, speed):
        moverequest = self.prepare_move_request()
        moverequest.Translation.PanTilt.x = 0
        moverequest.Translation.PanTilt.y = 0
        moverequest.Translation.Zoom = 0
        if zoom_in:
            moverequest.Translation.Zoom = speed
        else:
            moverequest.Translation.Zoom = -speed
        self.ptz.RelativeMove(moverequest)


class HikvisionCameraZoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('camera_id', openapi.IN_QUERY, description="ID of controlled camera", type=openapi.TYPE_INTEGER),
        openapi.Parameter('zoom_in', openapi.IN_QUERY, description="If True - camera will zoom in. It will zoom out otherwise", type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('speed', openapi.IN_QUERY, description="Speed of zoom", type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
    ])
    def list(self, request):
        camera_id = request.query_params.get('camera_id')
        zoom_in = request.query_params.get('zoom_in') == 'true'
        speed = request.query_params.get('speed')
        speed = float(speed) if speed else 0.1

        try:
            camera = Camera.objects.get(id=camera_id)
            ptz_controller = PTZController(camera)
            ptz_controller.zoom_camera(zoom_in, speed)
            return Response({'message': 'Camera zoom adjusted'})
        except Camera.DoesNotExist:
            return Response({'detail': 'Camera not found'}, status=404)
        except Exception as e:
            logger.error(f"Error adjusting zoom: {e}")
            return Response({'detail': 'Error adjusting zoom'}, status=500)


class HikvisionCameraPositionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('camera_id', openapi.IN_QUERY, description="ID of controlled camera", type=openapi.TYPE_INTEGER),
        openapi.Parameter('direction', openapi.IN_QUERY, description="LEFT, RIGHT, UP, DOWN", type=openapi.TYPE_STRING),
        openapi.Parameter('speed', openapi.IN_QUERY, description="Speed of movement", type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
    ])
    def list(self, request):
        camera_id = request.query_params.get('camera_id')
        direction = request.query_params.get('direction')
        speed = request.query_params.get('speed')

        if not camera_id or not direction:
            return Response({'detail': 'camera_id and direction are required'}, status=400)

        speed = float(speed) if speed else 0.005

        try:
            camera = Camera.objects.get(id=camera_id)
            ptz_controller = PTZController(camera)
            ptz_controller.move_camera(direction, speed)
            return Response({'message': 'Camera moved'})
        except Camera.DoesNotExist:
            return Response({'detail': 'Camera not found'}, status=404)
        except Exception as e:
            logger.error(f"Error moving camera: {e}")
            return Response({'detail': 'Error moving camera'}, status=500)