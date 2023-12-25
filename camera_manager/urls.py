from django.urls import path, include
from rest_framework import routers
from .views import (
    CameraViewSet, 
    LocationViewSet, 
    CameraViewSet, 
    GroupTypeViewSet, 
    CameraGroupViewSet, 
    CameraToGroupViewSet, 
    HikvisionCameraZoomViewSet,
    HikvisionCameraPositionViewSet,
)
from .views import ( 
    get_camera_view, 
)

router = routers.DefaultRouter()
router.register('cameras', CameraViewSet, basename='cameras-viewset')
router.register('locations', LocationViewSet, basename='locations-viewset')
router.register('group-type', GroupTypeViewSet ,basename='group-type-viewset')
router.register('camera-group', CameraGroupViewSet ,basename='camera-group-viewset')
router.register('camera-to-group', CameraToGroupViewSet ,basename='camera-to-group-viewset')
router.register('camera-position', HikvisionCameraPositionViewSet, basename='camera-position-viewset')
router.register('camera-zoom', HikvisionCameraZoomViewSet, basename='camera-zoom-viewset')

urlpatterns = [
    path('', include(router.urls)),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
]