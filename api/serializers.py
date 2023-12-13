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
        fields = ('id', 'camera_name', 'camera_ip', 'input_location', 'output_location', 'camera_description', 'camera_lon', 'camera_lat')

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
        fields = ('type_name',)

class CameraGroupSerializer(serializers.ModelSerializer):
    group_type = GroupTypeSerializer()
    cameras = serializers.SerializerMethodField()

    def get_cameras(self, obj):
        camera_to_group = CameraToGroup.objects.filter(group_id=obj)
        cameras = [camera.camera_id for camera in camera_to_group]
        return CameraSerializer(cameras, many=True).data

    class Meta:
        model = CameraGroup
        fields = ('id', 'group_name', 'group_type', 'cameras')

class CameraToGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraToGroup
        fields = '__all__'

