from rest_framework import serializers

class GeoJSONSerializer(serializers.Serializer):
    data = serializers.JSONField(help_text="GeoJSON data")
