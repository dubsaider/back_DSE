from django.urls import path, include
from rest_framework import routers
from .views import (
    DetectedObjectTypeViewSet, 
    CameraViewSet, 
    ObjectsDetectionLogViewSet, 
    LocationViewSet, 
    CameraViewSet, 
    GroupTypeViewSet, 
    CameraGroupViewSet, 
    CameraToGroupViewSet, 
)
from .views import ( 
    get_camera_view, 
)

router = routers.DefaultRouter()
router.register('detected-object-types', DetectedObjectTypeViewSet, basename='detected-object-types-viewset')
router.register('cameras', CameraViewSet, basename='cameras-viewset')
router.register('objects-detection-logs', ObjectsDetectionLogViewSet, basename='objects-detection-logs-viewset')
router.register('locations', LocationViewSet, basename='locations-viewset')
router.register('group-type', GroupTypeViewSet ,basename='group-type-viewset')
router.register('camera-group', CameraGroupViewSet ,basename='camera-group-viewset')
router.register('camera-to-group', CameraToGroupViewSet ,basename='camera-to-group-viewset')

urlpatterns = [
    path('viewsets/', include(router.urls)),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
    # path('gen/zA', generate_data, name='generate_data'),
]
