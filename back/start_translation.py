import os
import shutil
from camera_manager.models import (
            Camera,            
        )
from camera_manager.serializers import (
        CameraSerializer,      
    )
from camera_manager.views import get_camera_view

def delete_old_video():
    folder_to_delete = "cameras"
    folder_path = os.path.join(os.getcwd(), folder_to_delete)
    if not os.path.exists(folder_path):
        return
    shutil.rmtree(folder_path)

def start_translations():
    for camera in Camera.objects.filter(is_active=True):
        get_camera_view(pk=camera.pk, filename='stream.m3u8')
    


