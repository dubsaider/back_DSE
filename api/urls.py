from django.urls import path, include
from rest_framework import routers
from .views import (
    DetectedObjectTypeViewSet, 
    ObjectsDetectionLogViewSet,
    IncidentViewSet,
    ZoneStatsViewSet,
    CameraStatsViewSet,
)

router = routers.DefaultRouter()
router.register('detected-object-types', DetectedObjectTypeViewSet, basename='detected-object-types-viewset')
router.register('objects-detection-logs', ObjectsDetectionLogViewSet, basename='objects-detection-logs-viewset')
router.register('incident', IncidentViewSet, basename='incident-viewset')
router.register('zone-stats', ZoneStatsViewSet, basename='zone-stats-viewset')
router.register('camera-stats', CameraStatsViewSet, basename='camera-stats-viewset')

urlpatterns = [
    path('', include(router.urls)),
]
