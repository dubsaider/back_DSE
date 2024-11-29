from django.urls import path, include
from rest_framework import routers
from .views import (
    IncidentViewSet,
    ZoneStatViewSet,
    CameraStatViewSet,
    IncidentTypeViewSet,
)
import os
from django.urls import path
from .models import Incident
from django.http import HttpResponseNotFound
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound



router = routers.DefaultRouter()
router.register('incident', IncidentViewSet, basename='incident-viewset')
router.register('zone-stats', ZoneStatViewSet, basename='zone-stats-viewset')
router.register('camera-stats', CameraStatViewSet, basename='camera-stats-viewset')
router.register('incident-type', IncidentTypeViewSet, basename='incident-type-viewset')

def get_incident_view(request=None, pk=None, filename='stream.m3u8'):
    if not Incident.objects.filter(pk=pk).exists():
        return HttpResponseNotFound()

    hls_output_dir = os.path.join(Path(__file__).resolve().parent.parent, 'incidents')
    hls_output_dir = os.path.join(hls_output_dir, f'incident_{pk}') 
    
    if not os.path.exists(hls_output_dir):
        return HttpResponseNotFound()

    playlist_path = os.path.join(hls_output_dir, filename)
    if not os.path.exists(playlist_path):
        return HttpResponseNotFound("Файл плейлиста не найден.")

    with open(playlist_path, 'rb') as playlist_file:
        response = HttpResponse(playlist_file.read(), content_type='application/vnd.apple.mpegurl')
        return response

urlpatterns = [
    path('', include(router.urls)),
    path('incidents/<int:pk>/<str:filename>', get_incident_view, name='get_incident'),
]

