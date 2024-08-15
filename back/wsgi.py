"""
WSGI config for back project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

#from .start_translation import delete_old_video

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

#delete_old_video()

application = get_wsgi_application()
#Func after init
from .start_translation import delete_old_video
delete_old_video()
