from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime, timedelta
from .models import (
            IncidentType,
            Incident,
            ZoneStat,
            CameraStat,
            Camera
        )
from .serializers import (
        IncidentSerializer,
        ZoneStatSerializer,
        CameraStatSerializer,
        IncidentTypeSerializer,
    )
from rest_framework.permissions import (
        IsAuthenticated,
        IsAuthenticatedOrReadOnly
    )

def create_manual_parameters(**kwargs):
    pagination_parameters = [
        openapi.Parameter(
            name='page',
            in_=openapi.IN_QUERY,
            description='Номер страницы',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            name='page_size',
            in_=openapi.IN_QUERY,
            description='Размер страницы',
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ]

    parameters = pagination_parameters + [
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
    ]

    for name, description in kwargs.items():
        parameters.append(
            openapi.Parameter(
                name=name,
                in_=openapi.IN_QUERY,
                description=description,
                type=openapi.TYPE_INTEGER,
                required=False
            )
        )
    return parameters

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

class IncidentTypeViewSet(viewsets.ModelViewSet):
    queryset = IncidentType.objects.all()
    http_method_names = ['get']
    serializer_class = IncidentTypeSerializer

class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    http_method_names = ['get']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Incident.objects.all().order_by('-start_timestamp')
        camera_id = self.request.query_params.get('camera_id', None)
        if camera_id is not None:
            camera = get_object_or_404(Camera, id=camera_id)
            queryset = queryset.filter(camera=camera)

        start_datetime = self.request.query_params.get('start_datetime', None)
        end_datetime = self.request.query_params.get('end_datetime', None)
        if start_datetime is not None:
            queryset = queryset.filter(datetime__gte=datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S'))
        if end_datetime is not None:
            queryset = queryset.filter(datetime__lte=datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S'))

        incident_type = self.request.query_params.get('incident_type', None)
        if incident_type is not None:
            queryset = queryset.filter(incident_type=incident_type)

        is_system = self.request.query_params.get('is_system', None)
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system)
        else:
            queryset = queryset.filter(is_system=False)   
        return queryset
    
    @swagger_auto_schema(
        manual_parameters=create_manual_parameters(
            camera_id='ID of the camera to filter by',
            incident_type='Type of the incident to filter by'
        ),
        responses={200: openapi.Response('description', IncidentSerializer(many=True))}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ZoneStatViewSet(viewsets.ModelViewSet):
    queryset = ZoneStat.objects.all()
    serializer_class = ZoneStatSerializer
    http_method_names = ['get']
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
            manual_parameters=create_manual_parameters(location_id='ID of the location to filter by'),
            responses={200: openapi.Response('description', ZoneStatSerializer(many=True))})
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        start_datetime = request.query_params.get('start_datetime', None)
        end_datetime = request.query_params.get('end_datetime', None)
        location_id = request.query_params.get('location_id', None)

        if start_datetime is not None and end_datetime is not None:
            try:
                start_datetime = timezone.datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
                end_datetime = timezone.datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S')
                queryset = queryset.filter(timestamp__range=(start_datetime, end_datetime))
            except ValueError:
                return Response({"detail": "Invalid datetime format. Expected format is YYYY-MM-DDTHH:MM:SS."},
                                status=status.HTTP_400_BAD_REQUEST)

        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)

        queryset = queryset.order_by('timestamp')

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
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
            manual_parameters=create_manual_parameters(camera_id='ID of the camera to filter by')
            )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        camera_id = request.query_params.get('camera_id', None)
        start_datetime = request.query_params.get('start_datetime', None)
        end_datetime = request.query_params.get('end_datetime', None)

        if camera_id is not None:
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                return Response({"detail": "Camera with id {} does not exist.".format(camera_id)},
                                status=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(camera=camera)

        if start_datetime is not None and end_datetime is not None:
            try:
                start_datetime = timezone.datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
                end_datetime = timezone.datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S")
                queryset = queryset.filter(timestamp__range=(start_datetime, end_datetime))
            except ValueError:
                return Response({"detail": "Invalid datetime format. Expected format is YYYY-MM-DDTHH:MM:SS."},
                                status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.order_by('timestamp')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)