from rest_framework import serializers
from .models import (
    Model, 
    ComputerVisionModule,
    ProcessEvent, 
    Process
)

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class ComputerVisionModuleSerializer(serializers.ModelSerializer):
    model_type = ModelSerializer()

    class Meta:
        model = ComputerVisionModule
        fields = '__all__'

class ProcessEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessEvent
        fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    cv_module_id = serializers.StringRelatedField()
    camera_id = serializers.StringRelatedField()

    class Meta:
        model = Process
        fields = ['cv_module_id', 'camera_id', 'all_frames_event', 'any_object_event', 'any_object_few_minutes_event', 'result_url']