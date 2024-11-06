from django.urls import path, include
from rest_framework import routers
from .views import (
    CameraViewSet,
    StreamViewSet,
    LocationViewSet,
    CameraGroupViewSet,
    HikvisionCameraZoomViewSet,
    HikvisionCameraPositionViewSet,
)

router = routers.DefaultRouter()
router.register('cameras', CameraViewSet, basename='cameras-viewset')
router.register('stream', StreamViewSet, basename='stream-viewset')
router.register('locations', LocationViewSet, basename='locations-viewset')
router.register('camera-group', CameraGroupViewSet ,basename='camera-group-viewset')
router.register('camera-position', HikvisionCameraPositionViewSet, basename='camera-position-viewset')
router.register('camera-zoom', HikvisionCameraZoomViewSet, basename='camera-zoom-viewset')

urlpatterns = [
    path('', include(router.urls)),
]