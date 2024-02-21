from rest_framework import serializers
from .models import (
    IncidentType,
    Incident,
    ZoneStat,
    CameraStat
)
from camera_manager.serializers import (
    CameraSerializer,
    LocationSerializer,
)


class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        fields = '__all__'

class IncidentSerializer(serializers.ModelSerializer):
   camera = CameraSerializer()
   incident_type = IncidentTypeSerializer()

   class Meta:
       model = Incident
       fields = ['timestamp', 'camera', 'incident_type', 'link']

class ZoneStatSerializer(serializers.ModelSerializer):
   location = LocationSerializer()
   
   class Meta:
       model = ZoneStat
       fields = '__all__'

class CameraStatSerializer(serializers.ModelSerializer):
   camera = CameraSerializer()
   
   class Meta:
       model = CameraStat
       fields = ['timestamp', 'camera', 'input_value', 'output_value']
