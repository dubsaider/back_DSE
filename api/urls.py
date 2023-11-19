from django.urls import path
from .views import (
    CameraList, 
    ClusterUnitList, 
    ProcessingList, 
    ObjectsDetectionLogsList,

    create_camera,
    edit_camera,
    delete_camera,

    create_processing,
    edit_processing,
    delete_processing,

    create_location,
    edit_location,
    delete_location,

    create_cluster_unit,
    edit_cluster_unit,
    delete_cluster_unit,

    video_hls_view,
    get_camera_view,
    # generate_data,
)

urlpatterns = [
    path('camera/', CameraList.as_view(), name='camera-list'),
    path('camera/', create_camera, name='camera-create'),
    path('camera/<int:id>', edit_camera, name='camera-edit'),
    path('camera/<int:id>', delete_camera, name='camera-delete'),

    path('unit/', ClusterUnitList.as_view(), name='unit-list'),
    path('unit/', create_cluster_unit, name='unit-create'),
    path('unit/<int:id>', edit_cluster_unit, name='unit-edit'),
    path('unit/<int:id>', delete_cluster_unit, name='unit-delete'),

    path('processing/', ProcessingList.as_view(), name='processing-list'),
    path('processing/', create_processing, name='processing-create'),
    path('processing/<int:id>', edit_processing, name='processing-edit'),
    path('processing/<int:id>', delete_processing, name='processing-delete'),


    path('location/', create_location, name='location-create'),
    path('location/<int:id>', edit_location, name='location-edit'),
    path('location/<int:id>', delete_location, name='location-delete'),

    path('data/', ObjectsDetectionLogsList.as_view(), name='detected-objects-list'),
    path('video/<str:filename>', video_hls_view, name='video-hls'),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
    # path('gen/zA', generate_data, name='generate_data'),
]
