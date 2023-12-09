from rest_framework import serializers
from .models import (
    Model, 
    ComputerVisionModule,
    ProcessAction,
    ProcessEvent, 
    Process
)
from api.serializers import CameraSerializer

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class ComputerVisionModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerVisionModule
        fields = '__all__'

class ProcessActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessAction
        fields = '__all__'

class ProcessEventSerializer(serializers.ModelSerializer):
    actions = ProcessActionSerializer(many=True)

    def create(self, validated_data):
        actions = validated_data.pop('actions')
        event = ProcessEvent.objects.create(**validated_data)

        for action in actions:
            ProcessAction.objects.create(event=event, **action)
        
        return event

    class Meta:
        model = ProcessEvent
        fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    events = ProcessEventSerializer(many=True)

    def create(self, validated_data):
        events = validated_data.pop('events')
        # TODO fix stream url
        validated_data['result_url'] = 'url'
        process = Process.objects.create(**validated_data)

        for event in events:
            ProcessEvent.objects.create(process=process, **event)
        
        # TODO send message to Kafka topic

        return process

    class Meta:
        model = Process
        fields = '__all__'