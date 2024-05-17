from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status
from .models import JsonFile
from .serializers import FileSerializer
import json

class UploadJsonFileView(APIView):
    parser_class = (FileUploadParser,)

    def get(self, request, *args, **kwargs):
        latest_file = JsonFile.objects.latest("uploaded_at")
        
        if latest_file is not None:
            with open(latest_file.file.path, 'r') as f:
                data = json.load(f)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No files available'}, status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
