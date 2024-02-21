from django.urls import path, include
from rest_framework import routers
from .views import (
    IncidentViewSet,
    ZoneStatViewSet,
    CameraStatViewSet,
)

router = routers.DefaultRouter()
router.register('incident', IncidentViewSet, basename='incident-viewset')
router.register('zone-stats', ZoneStatViewSet, basename='zone-stats-viewset')
router.register('camera-stats', CameraStatViewSet, basename='camera-stats-viewset')

urlpatterns = [
    path('', include(router.urls)),
]
