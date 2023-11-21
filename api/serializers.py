from rest_framework import serializers
from .models import (
    Camera, 
    ClusterUnit, 
    Processing, 
    DetectedObjectType, 
    ObjectsDetectionLog,
    Process,
    ComputerVisionModule,
    ProcessEvent,
    Action,
    EventType
    )


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('camera_ip',)

class ClusterUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterUnit
        fields = '__all__'

class ProcessingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processing
        fields = '__all__'


class ObjectsDetectionLogSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.location')
    type = serializers.CharField(source='type.type')
    class Meta:
        model = ObjectsDetectionLog
        fields = '__all__'


class ComputerVisionModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerVisionModule
        fields = ('cv_modules_name',)

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('action_name', 'parameters',)


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ('event_name', )


class ProcessEventSerializer(serializers.ModelSerializer):
    actions = ActionSerializer(read_only=True, many=True)
    event = EventTypeSerializer()
    class Meta:
        model = ProcessEvent
        fields = ('event', 'actions', 'parameters')


class ProcessSerializer(serializers.ModelSerializer):
    # cv_module = ComputerVisionModuleSerializer()
    cv_modules_name = serializers.CharField(source='cv_module.cv_modules_name')

    process_events = ProcessEventSerializer(read_only=True, many=True)
    class Meta:
        model = Process
        fields = ('__all__')
        # fields = ('cv_module', )



