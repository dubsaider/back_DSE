from rest_framework import serializers
from .models import CameraPreset, CameraGroup, Camera, CameraModule, Role, User


class CameraPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraPreset
        fields = '__all__'


class CameraGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = '__all__'


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'


class CameraModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraModule
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
