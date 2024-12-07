from django.urls import path
from .views import UploadJsonFileView

urlpatterns = [
    path('', UploadJsonFileView.as_view(), name='geojson')
]
