from django.urls import path, include
from rest_framework import routers
from .views import (
    DetectedObjectTypeViewSet, 
    ObjectsDetectionLogViewSet,
)

router = routers.DefaultRouter()
router.register('detected-object-types', DetectedObjectTypeViewSet, basename='detected-object-types-viewset')
router.register('objects-detection-logs', ObjectsDetectionLogViewSet, basename='objects-detection-logs-viewset')

urlpatterns = [
    path('', include(router.urls)),
]
