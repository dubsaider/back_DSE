from django.urls import path
from .views import (
    CameraList, 
    ClusterUnitList, 
    ProcessingList, 
    ObjectsDetectionLogsList,

    edit_camera,
    del_camera,

    edit_processing,
    del_processing,

    edit_location,
    del_location,

    edit_cluster_unit,
    del_cluster_unit,

    video_hls_view,
    get_camera_view,
    # generate_data,
)

urlpatterns = [
    path('cameras/', CameraList.as_view(), name='camera-list'),
    path('cameras/edit', edit_camera, name='camera-edit'),
    path('cameras/delete', del_camera, name='camera-delete'),

    path('units/', ClusterUnitList.as_view(), name='unit-list'),
    path('units/edit', edit_cluster_unit, name='unit-edit'),
    path('units/delete', del_cluster_unit, name='unit-deleta'),

    path('processing/', ProcessingList.as_view(), name='processing-list'),
    path('processing/edit', edit_processing, name='processing-edit'),
    path('processing/delete', del_processing, name='processing-del'),

    path('location/edit', edit_location, name='location-edit'),
    path('location/delete', del_location, name='location-del'),

    path('data/', ObjectsDetectionLogsList.as_view(), name='detected-objects-list'),
    path('video/<str:filename>', video_hls_view, name='video-hls'),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
    # path('gen/zA', generate_data, name='generate_data'),
]
