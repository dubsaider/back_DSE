from django.urls import path, include
from rest_framework import routers
from .views import (
    ModelViewSet,
    ComputerVisionModuleViewSet,
    ProcessActionViewSet,
    ProcessEventViewSet,
    ProcessingViewSet,
)
from api.urls import router

router.register('model', ModelViewSet, basename='model-viewset')
router.register('computer-vision-modules', ComputerVisionModuleViewSet, basename='computer-vision-modules-viewset')
router.register('process-action', ProcessActionViewSet, basename='process-action-viewset')
router.register('process-event', ProcessEventViewSet, basename='process-event-viewset')
router.register('group-type', ProcessingViewSet ,basename='group-type-viewset')

urlpatterns = [
    path('viewsets/', include(router.urls)),
    # path('gen/zA', generate_data, name='generate_data'),
]