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
    action_type = ActionTypeSerializer()

    class Meta:
        model = ProcessAction
        fields = '__all__'

class ProcessEventSerializer(serializers.ModelSerializer):
    actions = ProcessActionSerializer(many=True)
    event_type = EventTypeSerializer()

    class Meta:
        model = ProcessEvent
        fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    events = ProcessEventSerializer(many=True)
    cv_module = ComputerVisionModuleSerializer()
    camera_id = serializers.PrimaryKeyRelatedField(source='camera', read_only=True)

    class Meta:
        model = Process
        fields = ('cv_module', 'camera_id', 'events', 'result_url')