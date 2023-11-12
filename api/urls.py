from django.urls import path
from .views import (
    CameraList, 
    ClusterUnitList, 
    ProcessingList, 
    ObjectsDetectionLogsList,
    edit_camera,
    del_camera,
    video_hls_view,
    get_camera_view,
    # generate_data,
)

urlpatterns = [
    path('cameras/', CameraList.as_view(), name='camera-list'),
    path('cameras/edit', edit_camera, name='camera-edit'),
    path('cameras/delete', del_camera, name='camera-delete'),
    path('units/', ClusterUnitList.as_view(), name='unit-list'),
    path('processing/', ProcessingList.as_view(), name='processing-list'),
    path('data/', ObjectsDetectionLogsList.as_view(), name='detected-objects-list'),
    path('video/<str:filename>', video_hls_view, name='video-hls'),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
    # path('gen/zA', generate_data, name='generate_data'),
]
