from django.urls import path
from . import views
from .views import CameraList, ClusterUnitList, ProcessingList, ObjectsDetectionLogsList


urlpatterns = [
    path('ser', views.test),
    path('cameras/', CameraList.as_view(), name='camera-list'),
    path('units/', ClusterUnitList.as_view(), name='unit-list'),
    path('processing/', ProcessingList.as_view(), name='processing-list'),
    path('data/', ObjectsDetectionLogsList.as_view(), name='detected-objects-list'),
#    path('data/by-datestamp', ObjectsDetectionLogsRange.as_view(), name='detected-objects-by-datestamp'),
]
