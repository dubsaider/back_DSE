from rest_framework import serializers
from.models import JsonFile

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonFile
        fields = ['id', 'file']
