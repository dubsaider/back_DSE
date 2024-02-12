from rest_framework import serializers
from .models import (
    DetectedObjectType, 
    ObjectsDetectionLog,
    Incident,
    ZoneStats,
)
from camera_manager.serializers import (
    CameraSerializer
)


class ObjectsDetectionLogSerializer(serializers.ModelSerializer):
    start_datestamp = serializers.DateTimeField(write_only=True, required=False)
    end_datestamp = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = ObjectsDetectionLog
        fields = '__all__'

class DetectedObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedObjectType
        fields = '__all__'

class IncidentSerializer(serializers.ModelSerializer):
   camera = CameraSerializer()

   class Meta:
       model = Incident
       fields = ['timestamp', 'camera', 'event', 'incident', 'link']

class ZoneStatsSerializer(serializers.ModelSerializer):
   camera = CameraSerializer()
   
   class Meta:
       model = ZoneStats
       fields = ['timestamp', 'camera', 'location', 'change']

