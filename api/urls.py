from django.contrib import admin
from django.urls import path
from backend.views import (
    CameraPresetListCreateView,
    CameraPresetDetailView,
    CameraGroupListCreateView,
    CameraGroupDetailView,
    CameraListCreateView,
    CameraDetailView,
    CameraModuleListCreateView,
    CameraModuleDetailView,
    RoleListCreateView,
    RoleDetailView,
    UserListCreateView,
    UserDetailView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('camera_presets/', CameraPresetListCreateView.as_view(),
         name='camera_preset_list_create'),
    path('camera_presets/<int:pk>/', CameraPresetDetailView.as_view(),
         name='camera_preset_detail'),
    path('camera_groups/', CameraGroupListCreateView.as_view(),
         name='camera_group_list_create'),
    path('camera_groups/<int:pk>/', CameraGroupDetailView.as_view(),
         name='camera_group_detail'),
    path('cameras/', CameraListCreateView.as_view(), name='camera_list_create'),
    path('cameras/<int:pk>/', CameraDetailView.as_view(), name='camera_detail'),
    path('camera_modules/', CameraModuleListCreateView.as_view(),
         name='camera_module_list_create'),
    path('camera_modules/<int:pk>/', CameraModuleDetailView.as_view(),
         name='camera_module_detail'),
    path('roles/', RoleListCreateView.as_view(), name='role_list_create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),
    path('users/', UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

]
