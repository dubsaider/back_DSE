import os
import subprocess
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from datetime import datetime
from .models import (
            Camera, 
            ClusterUnit, 
            Processing, 
            ObjectsDetectionLogs,
        )
from .serializers import (
        CameraSerializer, 
        ClusterUnitSerializer, 
        ProcessingSerializer, 
        ObjectsDetectionLogsSerializer,
    )


class CameraList(generics.ListCreateAPIView):
    quaryset = Camera.objects.all()
    serializer_class = CameraSerializer

class ClusterUnitList(generics.ListCreateAPIView):
    queryset = ClusterUnit.objects.all()
    serializer_class = ClusterUnitSerializer

class ProcessingList(generics.ListCreateAPIView):
    queryset = Processing.objects.all()
    serializer_class = ProcessingSerializer

class ObjectsDetectionLogsList(generics.ListCreateAPIView):
    serializer_class = ObjectsDetectionLogsSerializer

    def get_queryset(self):
        queryset = ObjectsDetectionLogs.objects.all()

        start_datestamp = self.request.query_params.get('start_datestamp', None)
        end_datestamp = self.request.query_params.get('end_datestamp', None)
        location = self.request.query_params.get('location', None)
        detection_type = self.request.query_params.get('type', None)

        if start_datestamp:
            start_datestamp = datetime.strptime(start_datestamp, "%Y-%m-%dT%H:%M:%S")
            queryset = queryset.filter(datestamp__gte=start_datestamp)

        if end_datestamp:
            end_datestamp = datetime.strptime(end_datestamp, "%Y-%m-%dT%H:%M:%S")
            queryset = queryset.filter(datestamp__lte=end_datestamp)

        if location:
            queryset = queryset.filter(location__location=location)
        

        if detection_type:
            queryset = queryset.filter(type__type=detection_type)

        return queryset
    
def video_hls_view(request, filename):
    # video = get_object_or_404(Video, id=video_id)

    # video_path = video.video_file.path
    video_path = '/home/ubuntuser/back_DSE/vid/L.mp4'

    hls_output_dir = os.path.join(os.path.dirname(video_path), 'test')

    #os.makedirs(hls_output_dir, exist_ok=True)

    # subprocess.run([
    #     'ffmpeg',
    #     '-i', video_path,
    #     '-c:v', 'libx264',
    #     '-c:a', 'aac',
    #     '-hls_time', '20',
    #     '-hls_list_size', '10',
    #     '-hls_flags', 'delete_segments',
    #     '-hls_segment_filename', os.path.join(hls_output_dir, 'segment%d.ts'),
    #     os.path.join(hls_output_dir, 'playlist.m3u8'),
    # ])

    playlist_path = os.path.join(hls_output_dir, filename)

    with open(playlist_path, 'rb') as playlist_file:
        response = HttpResponse(playlist_file.read(), content_type='application/vnd.apple.mpegurl')
        return response
