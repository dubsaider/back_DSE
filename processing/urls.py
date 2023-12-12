from django.urls import path, include
from rest_framework import routers
from .views import (
    ModelViewSet,
    ComputerVisionModuleViewSet,
    ProcessEventViewSet,
    ProcessingViewSet,
)

router = routers.DefaultRouter()
router.register('model', ModelViewSet, basename='model-viewset')
router.register('computer-vision-modules', ComputerVisionModuleViewSet, basename='computer-vision-modules-viewset')
router.register('process-event', ProcessEventViewSet, basename='process-event-viewset')
router.register('processing', ProcessingViewSet ,basename='processing-viewset')

urlpatterns = [
    path('processing/', include(router.urls)),
    # path('gen/zA', generate_data, name='generate_data'),
]