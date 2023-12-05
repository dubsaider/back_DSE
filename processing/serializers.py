from rest_framework import serializers
from .models import (
    Model, 
    ComputerVisionModule, 
    ProcessAction, 
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
    cv_module_id = ComputerVisionModuleSerializer()
    process_events = ProcessEventSerializer(many=True)

    class Meta:
        model = Process
        fields = '__all__'