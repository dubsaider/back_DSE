from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime, timedelta
from .models import (
            Incident,
            ZoneStat,
            CameraStat,
            Camera
        )
from .serializers import (
        IncidentSerializer,
        ZoneStatSerializer,
        CameraStatSerializer,
    )
from rest_framework.permissions import (
        IsAuthenticated,
        IsAuthenticatedOrReadOnly
    )

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    http_method_names = ['get']


class ZoneStatViewSet(viewsets.ModelViewSet):
    queryset = ZoneStat.objects.all()
    serializer_class = ZoneStatSerializer
    http_method_names = ['get']


class CameraStatViewSet(viewsets.ModelViewSet):
    queryset = CameraStat.objects.all()
    serializer_class = CameraStatSerializer
    http_method_names = ['get']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            name='camera_id',
            in_=openapi.IN_QUERY,
            description='ID of the camera to filter by',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            name='date_range',
            in_=openapi.IN_QUERY,
            description='Date range to filter by in the format YYYY-MM-DD,YYYY-MM-DD',
            type=openapi.TYPE_STRING,
            required=False
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CameraStat.objects.all()

        camera_id = self.request.query_params.get('camera_id', None)
        date_range = self.request.query_params.get('date_range', None)

        if camera_id is not None:
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                return Response({"detail": "Camera with id {} does not exist.".format(camera_id)},
                                status=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(camera=camera)

        if date_range is not None:
            try:
                start_date, end_date = date_range.split(',')
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(timestamp__range=(start_date, end_date))
            except ValueError:
                return Response({"detail": "Invalid date range format. Expected format is YYYY-MM-DD,YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            queryset = queryset.filter(timestamp__range=(start_date, end_date))

        return queryset