from django.urls import path
from .views import (
    CameraList, 
    ClusterUnitList, 
    ProcessingList, 
    ObjectsDetectionLogsList,
    video_hls_view
)

urlpatterns = [
    path('cameras/', CameraList.as_view(), name='camera-list'),
    path('units/', ClusterUnitList.as_view(), name='unit-list'),
    path('processing/', ProcessingList.as_view(), name='processing-list'),
    path('data/', ObjectsDetectionLogsList.as_view(), name='detected-objects-list'),
    path('video/<str:filename>', video_hls_view, name='video-hls')
]
