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

# class ProcessSerializer(serializers.ModelSerializer):
#     cv_module_id = ComputerVisionModuleSerializer()
#     process_events = ProcessEventSerializer(many=True)

#     class Meta:
#         model = Process
#         fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    cv_module_id = serializers.StringRelatedField()
    camera_id = serializers.StringRelatedField()
    process_events = serializers.StringRelatedField(many=True)

    class Meta:
        model = Process
        fields = ['id', 'cv_module_id', 'camera_id', 'process_events', 'result_url']