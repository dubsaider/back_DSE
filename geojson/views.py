from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from .serializers import GeoJSONSerializer
import json

class GeoJSONView(APIView):
    @swagger_auto_schema(responses={
        200: GeoJSONSerializer(),
        400: 'Bad Request',
        404: 'File not found',
    })
    def get(self, request):
        try:
            with open('./geojson/file.geojson', 'r') as file:
                data = json.load(file)
            return Response(data)
        except FileNotFoundError:
            return Response({"error": "File not found"}, status=404)

    @swagger_auto_schema(responses={
        200: 'File updated successfully',
        400: 'Bad Request',
    })
    def post(self, request):
        serializer = GeoJSONSerializer(data=request.data)
        if serializer.is_valid():
            with open('./geojson/file.geojson', 'w') as file:
                json.dump(serializer.validated_data['data'], file)
            return Response({"message": "File updated successfully"}, status=200)
        return Response(serializer.errors, status=400)
