from django.urls import path, include
from rest_framework import routers
from .views import (
    IncidentViewSet,
    ZoneStatViewSet,
    CameraStatViewSet,
    IncidentTypeViewSet,
)

router = routers.DefaultRouter()
router.register('incident', IncidentViewSet, basename='incident-viewset')
router.register('zone-stats', ZoneStatViewSet, basename='zone-stats-viewset')
router.register('camera-stats', CameraStatViewSet, basename='camera-stats-viewset')
router.register('incident-type', IncidentTypeViewSet, basename='incident-type-viewset')


urlpatterns = [
    path('', include(router.urls)),
]
