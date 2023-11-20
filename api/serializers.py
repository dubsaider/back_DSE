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
    DetectedObjectType
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