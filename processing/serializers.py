from rest_framework import serializers
from .models import (
    Model, 
    ComputerVisionModule,
    ActionType,
    EventType,
    ProcessAction,
    ProcessEvent, 
    Process
)
from camera_manager.serializers import CameraSerializer

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class ComputerVisionModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerVisionModule
        fields = ['id', 'cv_modules_name', 'cv_modules_description', 'model_type']

class ActionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionType
        fields = '__all__'

class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
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
    cv_module_id = ComputerVisionModuleSerializer()
    camera_id = CameraSerializer()

    class Meta:
        model = Process
        fields = '__all__'