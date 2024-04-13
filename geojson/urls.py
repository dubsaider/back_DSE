from django.urls import path
from .views import GeoJSONView

urlpatterns = [
    path('', GeoJSONView.as_view(), name='geojson')
]
