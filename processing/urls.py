from django.urls import path, include
from rest_framework import routers
from .views import (
    ModelViewSet,
    ComputerVisionModuleViewSet,
    ProcessEventViewSet,
    ProcessingViewSet,
    EventTypeViewSet,
    ActionTypeViewSet,
)

router = routers.DefaultRouter()
router.register('model', ModelViewSet, basename='model-viewset')
router.register('computer-vision-modules', ComputerVisionModuleViewSet, basename='computer-vision-modules-viewset')
router.register('process-event', ProcessEventViewSet, basename='process-event-viewset')
router.register('processing', ProcessingViewSet, basename='processing-viewset')
router.register('event-type', EventTypeViewSet, basename='event-type-viewset')
router.register('action-type', ActionTypeViewSet, basename='action-type-viewset')

urlpatterns = [
    path('', include(router.urls)),
    # path('gen/zA', generate_data, name='generate_data'),
]