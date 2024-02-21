from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
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
    pagination_class = PageNumberPagination

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            name='start_datetime',
            in_=openapi.IN_QUERY,
            description='Start datetime to filter by in the format YYYY-MM-DDTHH:MM:SS',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            name='end_datetime',
            in_=openapi.IN_QUERY,
            description='End datetime to filter by in the format YYYY-MM-DDTHH:MM:SS',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            name='location_id',
            in_=openapi.IN_QUERY,
            description='ID of the location to filter by',
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Фильтрация по дате и времени и локации
        start_datetime = request.query_params.get('start_datetime', None)
        end_datetime = request.query_params.get('end_datetime', None)
        location_id = request.query_params.get('location_id', None)

        if start_datetime is not None and end_datetime is not None:
            start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
            end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')
            queryset = queryset.filter(timestamp__range=(start_datetime, end_datetime))

        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

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
            name='start_datetime',
            in_=openapi.IN_QUERY,
            description='Start datetime to filter by in the format YYYY-MM-DDTHH:MM:SS',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            name='end_datetime',
            in_=openapi.IN_QUERY,
            description='End datetime to filter by in the format YYYY-MM-DDTHH:MM:SS',
            type=openapi.TYPE_STRING,
            required=False
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CameraStat.objects.all()

        camera_id = self.request.query_params.get('camera_id', None)
        start_datetime = self.request.query_params.get('start_datetime', None)
        end_datetime = self.request.query_params.get('end_datetime', None)

        if camera_id is not None:
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                return Response({"detail": "Camera with id {} does not exist.".format(camera_id)},
                                status=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(camera=camera)

        if start_datetime is not None and end_datetime is not None:
            try:
                start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
                end_datetime = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S")
                queryset = queryset.filter(timestamp__range=(start_datetime, end_datetime))
            except ValueError:
                return Response({"detail": "Invalid datetime format. Expected format is YYYY-MM-DDTHH:MM:SS."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            end_datetime = datetime.now()
            start_datetime = end_datetime - timedelta(days=1)
            queryset = queryset.filter(timestamp__range=(start_datetime, end_datetime))

        return queryset