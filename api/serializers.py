from rest_framework import serializers
from .models import (
    Camera, 
    ClusterUnit, 
    Processing, 
    DetectedObjectType, 
    ObjectsDetectionLog,
    Location,
    EventType,
    Action,
    Model,
    ComputerVisionModule,
    Event,
    Process,
    ProcessEvent,
    GroupType,
    CameraGroup,
    CameraToGroup
)


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'

class ClusterUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterUnit
        fields = '__all__'

class ProcessingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processing
        fields = '__all__'

class ObjectsDetectionLogSerializer(serializers.ModelSerializer):
    start_datestamp = serializers.DateTimeField(write_only=True, required=False)
    end_datestamp = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = ObjectsDetectionLog
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
     class Meta:
        model = Location
        fields = '__all__'

class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class ComputerVisionModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerVisionModule
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class DetectedObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedObjectType
        fields = '__all__'

class ActionSerializerForProcessEvent(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('action_name', 'parameters',)


class ProcessEventSerializer(serializers.ModelSerializer):
    actions = ActionSerializerForProcessEvent(read_only=True, many=True)
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


class GroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupType
        fields = '__all__'

class CameraGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = '__all__'

class CameraToGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraToGroup
        fields = '__all__'

