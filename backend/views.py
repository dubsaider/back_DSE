from rest_framework import generics
from .models import CameraPreset, CameraGroup, Camera, CameraModule, Role, User
from .serializers import (
    CameraPresetSerializer,
    CameraGroupSerializer,
    CameraSerializer,
    CameraModuleSerializer,
    RoleSerializer,
    UserSerializer,
)


class CameraPresetListCreateView(generics.ListCreateAPIView):
    queryset = CameraPreset.objects.all()
    serializer_class = CameraPresetSerializer


class CameraPresetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CameraPreset.objects.all()
    serializer_class = CameraPresetSerializer


class CameraGroupListCreateView(generics.ListCreateAPIView):
    queryset = CameraGroup.objects.all()
    serializer_class = CameraGroupSerializer


class CameraGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CameraGroup.objects.all()
    serializer_class = CameraGroupSerializer


class CameraListCreateView(generics.ListCreateAPIView):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraModuleListCreateView(generics.ListCreateAPIView):
    queryset = CameraModule.objects.all()
    serializer_class = CameraModuleSerializer


class CameraModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CameraModule.objects.all()
    serializer_class = CameraModuleSerializer


class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
