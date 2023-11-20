from django.urls import path
from .views import (
    CameraList, 
    ClusterUnitList, 
    ProcessingList, 
    ObjectsDetectionLogsList,
    video_hls_view,
    get_camera_view,
    camera_methods,

    my_handler,
    # generate_data,
)

urlpatterns = [
    path('testing/', my_handler, name='test'),

    path('cameras/', camera_methods, name='camera-list'), #views.camerafunctions
    path('cameras/<int:id>', camera_methods, name='camera-single'),
    path('units/', ClusterUnitList.as_view(), name='unit-list'),
    # path('units/<int:id>', ClusterUnitList.as_view(), name='unit-conf'),
    path('processing/', ProcessingList.as_view(), name='processing-list'), # Для просмотра списка
    # path('processing/<int:id>', ProcessingList.as_view(), name='processing-conf'), # Для просмотра одной записи
    path('data/', ObjectsDetectionLogsList.as_view(), name='detected-objects-list'),
    path('video/<str:filename>', video_hls_view, name='video-hls'),
    path('camera/<int:pk>/<str:filename>', get_camera_view, name='get_camera'),
    # path('gen/zA', generate_data, name='generate_data'),
]
