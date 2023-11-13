import os
import random
from pathlib import Path
import subprocess
import math
import ffmpeg_streaming
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import generics
from datetime import datetime, timedelta
from .models import (
            Camera, 
            ClusterUnit, 
            Processing,
            Location,
            DetectedObjectType,
            ObjectsDetectionLog,
        )
from .serializers import (
        CameraSerializer, 
        ClusterUnitSerializer, 
        ProcessingSerializer, 
        ObjectsDetectionLogSerializer,
    )


class CameraList(generics.ListCreateAPIView):
    # quaryset = Camera.objects.all()
    serializer_class = CameraSerializer

    def get_queryset(self):
        return Camera.objects.all()

class ClusterUnitList(generics.ListCreateAPIView):
    queryset = ClusterUnit.objects.all()
    serializer_class = ClusterUnitSerializer

class ProcessingList(generics.ListCreateAPIView):
    queryset = Processing.objects.all()
    serializer_class = ProcessingSerializer

class ObjectsDetectionLogsList(generics.ListCreateAPIView):
    serializer_class = ObjectsDetectionLogSerializer

    def get_queryset(self):
        queryset = ObjectsDetectionLog.objects.all()

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
            if location.isnumeric():
                queryset = queryset.filter(location__pk=location)
            else:
                queryset = queryset.filter(location__location=location)
        

        if detection_type:
            queryset = queryset.filter(type__type=detection_type)

        return queryset.order_by('datestamp')

def edit_camera(self):
    id = self.request.query_params.get('id', None)
    ip = self.request.query_params.get('camera_ip', None)
    name = self.request.query_params.get('camera_name', None)
    in_loc = self.request.query_params.get('input_location', None)
    out_loc = self.request.query_params.get('output_location', None)
    description = self.request.query_params.get('description', None)

    if id is not None:
        if ip is None or\
           in_loc is None or\
           name is None:
            return HttpResponseNotFound()
        
        Camera.objects.create(camera_ip=ip,
                              camera_name=name,
                              input_location=Location.objects.filter(pk=in_loc).first(),
                              output_location=Location.objects.filter(pk=out_loc).first() if out_loc is not None else None,
                              camera_description=description if description is not None else "",
                              )
    else:
        camera = Camera.objects.filter(pk=id).first()
        if not camera:
            return HttpResponseNotFound() 
        if ip is not None:
            camera.camera_ip=ip
        if name is not None:
            camera.camera_name=name
        if in_loc is not None:
            Location.objects.filter(pk=in_loc).first()
        if out_loc is not None:
            Location.objects.filter(pk=out_loc).first()
        if description is not None:
            camera.camera_description=description
        camera.save()

def del_camera(self):
    id = self.request.query_params.get('id', None)
    if id is None:
        return HttpResponseNotFound()
    camera = Camera.objects.filter(pk=id).delete()
    
def video_hls_view(request, filename):
    # video = get_object_or_404(Video, id=video_id)

    # video_path = video.video_file.path
    video_path = '/home/ubuntuser/back_DSE/vid/L.mp4'

    hls_output_dir = os.path.join(os.path.dirname(video_path), 'test')
    # hls_output_dir = os.path.join(os.path.dirname(video_path), 'script_rtp')

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
    #     os.path.res
    playlist_path = os.path.join(hls_output_dir, filename)

    with open(playlist_path, 'rb') as playlist_file:
        response = HttpResponse(playlist_file.read(), content_type='application/vnd.apple.mpegurl')
        return response


ACTIVE_STREAMS = {}

def start_stream(ip, hls_output_dir, pk):
    stream_output_dir = os.path.join(hls_output_dir, 'stream.m3u8')
    video = ffmpeg_streaming.input(f'rtsp://admin:bvrn2022@{ip}:554/ISAPI/Streaming/Channels/101')
    hls_stream = video.hls(ffmpeg_streaming.Formats.h264(), hls_list_size = 10)
    # _480p  = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(854, 480), ffmpeg_streaming.Bitrate(750 * 1024, 192 * 1024))
    # hls_stream.representations(_480p)
    _720p = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(1280, 720), ffmpeg_streaming.Bitrate(2048 * 1024, 320 * 1024))
    hls_stream.representations(_720p)
    # _1080p = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(1920, 1080), ffmpeg_streaming.Bitrate(4096 * 1024, 320 * 1024))
    # hls_stream.representations(_1080p)
    hls_stream.flags('delete_segments')
    if not os.path.isfile(stream_output_dir):
        hls_stream.output(f'cameras/camera_{pk}/stream.m3u8')
    return hls_stream

    
def get_camera_view(request, pk, filename):
    
    if not Camera.objects.filter(pk=pk).exists():
        return HttpResponseNotFound()
    

    camera_ip = Camera.objects.filter(pk=pk).first().camera_ip
    hls_output_dir = os.path.join(Path(__file__).resolve().parent.parent, 'cameras')
    hls_output_dir = os.path.join(hls_output_dir, f'camera_{pk}')

    if f'camera_{pk}' not in ACTIVE_STREAMS.keys():
        if not os.path.exists(hls_output_dir):
            os.makedirs(hls_output_dir)
        
        

        ACTIVE_STREAMS[f'camera_{pk}'] = start_stream(camera_ip, hls_output_dir, pk)

    playlist_path = os.path.join(hls_output_dir, filename)

    with open(playlist_path, 'rb') as playlist_file:
        response = HttpResponse(playlist_file.read(), content_type='application/vnd.apple.mpegurl')
        return response

# def generate_data(request):

#     t_pk = 1
#     l_pk = 8
#     # a = datetime(2023, 8, 24)
#     # data =  ObjectsDetectionLog.objects.all().exclude(location__pk=32).filter(datestamp__gte=a).delete()
#     # a = datetime(2023, 8, 23)
#     # data =  ObjectsDetectionLog.objects.all().exclude(location__pk=32).filter(datestamp__gte=a)


#     # a = datetime(2023, 8, 30)
#     # t = timedelta(days=7)
#     # for log in data:
#     #      ObjectsDetectionLog(datestamp=log.datestamp + t,
#     #                         location=log.location,
#     #                         type=log.type,
#     #                         count=max(log.count * (1.02 - random.random() * 0.04), 0)).save()
    

#     # t = timedelta(days=7, hours=-1)
#     # a = datetime(2023, 8, 23)
#     # data =  ObjectsDetectionLog.objects.all().filter(location__pk=32).filter(datestamp__gte=a)
#     # for log in data:
#     #      ObjectsDetectionLog(datestamp=log.datestamp + t,
#     #                         location=log.location,
#     #                         type=log.type,
#     #                         count=log.count).save()
         
#     # def f_g1(x):
#     #     return int(-0.0002*x**6 + 0.014*x**5 - 0.3753*x**4 + 4.2678*x**3 - 18.093*x**2 + 23.44*x)

#     # def ran(x):
#     #     return int(((x/4) * math.cos(x)*math.sin(x**2)**3)**2 * math.sin(x) - math.cos(x)) 

#     ObjectsDetectionLog.objects.filter(location=Location.objects.filter(pk=l_pk).first()).delete()

#     sum = [-1, -2]
#     x_0 = 8

#     a = datetime(2023, 8, 23)
#     timeer = int(24 * 60 * 60 / 5) - 2

#     if (ObjectsDetectionLog.objects.filter(location=l_pk).count() < 17000):

#         for i in range(timeer):
#             sum[i % 2] = max(int(f_g1(x_0) * 13.031), 0)
#             if (x_0 > 6 and x_0 < 15.5): 
#                 # sum[i % 2] =  int(math.sin(x_0 - 1) * 300  - math.sin(x_0 - 3) * 3500 -  ran(x_0 + 2) * 0.4 - abs(min(x_0 - 10.5, 0) ) * 20 + abs(min(x_0 - 9, 0) ) * 700 + abs(min(x_0 - 8.5, 0) ) * 80)  + 13525
#                 # sum[i % 2] =  max(int(sum[i % 2] -  ran(x_0 + 3) * 0.03  - math.sin(x_0 - 6) * 2), 0) 
#             if (x_0 < 3): 
#                 sum[i % 2] = max(sum[i % 2] - 50, 0)
#             # sum[i % 2] = min(sum[i % 2] , 35)
#             x_0 += 1/3226
#             a = a + timedelta(seconds=5)

#             if (sum[(i + 1) % 2] != sum[i % 2]):
#                 ObjectsDetectionLog(datestamp=a,
#                                     location=Location.objects.filter(pk=l_pk).first(),
#                                     type=DetectedObjectType.objects.filter(pk=t_pk).first(),
#                                     count=sum[i % 2]).save()
