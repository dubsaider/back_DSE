from django.urls import path, include
from rest_framework import routers
from .views import (
    EventTypeViewSet, ActionViewSet, ModelsViewSet, ComputerVisionModulesViewSet, EventViewSet, DetectedObjectTypeViewSet, CameraViewSet, ObjectsDetectionLogViewSet, ClusterUnitViewSet, ProcessingViewSet, LocationViewSet, CameraViewSet
)
from .views import ( video_hls_view, get_camera_view )

router = routers.DefaultRouter()
router.register('event-types', EventTypeViewSet, basename='event-types-viewset')
router.register('actions', ActionViewSet, basename='actions-viewset')
router.register('models', ModelsViewSet, basename='models-viewset')
router.register('computer-vision-modules', ComputerVisionModulesViewSet, basename='computer-vision-modules-viewset')
router.register('events', EventViewSet, basename='events-viewset')
router.register('detected-object-types', DetectedObjectTypeViewSet, basename='detected-object-types-viewset')
router.register('cameras', CameraViewSet, basename='cameras-viewset')
router.register('objects-detection-logs', ObjectsDetectionLogViewSet, basename='objects-detection-logs-viewset')
router.register('cluster-units', ClusterUnitViewSet, basename='cluster-units-viewset')
router.register('processings', ProcessingViewSet, basename='processings-viewset')
router.register('locations', LocationViewSet, basename='locations-viewset')

urlpatterns = [
    path('viewsets/', include(router.urls)),
    path('video/<str:filename>', video_hls_view, name='video-hls'),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
    # path('gen/zA', generate_data, name='generate_data'),
]
