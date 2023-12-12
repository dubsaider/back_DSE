from rest_framework import serializers
from .models import (
    Model, 
    ComputerVisionModule,
    ProcessAction,
    ProcessEvent, 
    Process
)
from api.serializers import CameraSerializer

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class ComputerVisionModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerVisionModule
        fields = '__all__'

class ProcessActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessAction
        fields = '__all__'

class ProcessEventSerializer(serializers.ModelSerializer):
    actions = ProcessActionSerializer(many=True)

    class Meta:
        model = ProcessEvent
        fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    events = ProcessEventSerializer(many=True)

    class Meta:
        model = Process
        fields = '__all__'