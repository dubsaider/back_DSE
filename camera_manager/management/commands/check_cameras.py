from django.core.management.base import BaseCommand
from camera_manager.models import Camera
from api.models import Incident, IncidentType
import aiohttp
import asyncio
import logging
from asgiref.sync import sync_to_async
from utils.k8s_utils import get_k8s_apis, get_secrets
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Updating camera status data in the database"

    def get_incident_type(self, is_active):
        return IncidentType.objects.get(name='Изменение статуса камеры на "Активный"') if is_active else IncidentType.objects.get(name='Изменение статуса камеры на "Неактивный"')

    async def check_camera(self, session, obj, username, password):
        ip = obj.camera_ip
        status = obj.is_active
        new_status = False
        if ip == '0.0.0.0':
            new_status = False
            logger.warning(f'[WARNING] Camera {ip} has invalid IP address. Marking as inactive.')
        else:
            try:
                auth = aiohttp.BasicAuth(login=username, password=password)
                async with session.get(f"http://{ip}:554", timeout=5, auth=auth) as response:
                    new_status = response.status == 200
                    logger.info(f'[INFO] Camera {ip} is reachable.')
            except asyncio.TimeoutError:
                logger.warning(f'[WARNING] Camera check timed out: {ip}')
                new_status = False
            except aiohttp.ClientConnectionError:
                logger.warning(f'[WARNING] Camera connection error: {ip}')
                new_status = True
            except aiohttp.ClientResponseError as e:
                if e.status == 401:
                    logger.warning(f'[WARNING] Camera requires authorization: {ip}')
                    new_status = True
                else:
                    logger.warning(f'[WARNING] Camera check failed: {e}')
                    new_status = False

        await self.update_camera_status(obj, ip, status, new_status)

    async def update_camera_status(self, camera, ip, old_status, new_status):
        if old_status != new_status:
            incident_type = self.incident_type_active if new_status else self.incident_type_inactive
            new_incident = Incident(
                camera=camera,
                incident_type=incident_type,
                link=""
            )
            await sync_to_async(new_incident.save)()
            logger.info(f'[INFO] Camera {ip} status changed to {"Active" if new_status else "Inactive"}. Incident created.')
            await sync_to_async(Camera.objects.filter(pk=camera.pk).update)(is_active=new_status)
            logger.info(f'[INFO] Camera {ip} status updated in the database.')
        else:
            logger.info(f'[INFO] Camera {ip} status remains the same.')

    async def run_checks(self):
        logger.info('[INFO] Starting camera status check...')
        try:
            self.incident_type_active = await sync_to_async(self.get_incident_type)(True)
            self.incident_type_inactive = await sync_to_async(self.get_incident_type)(False)
        except IncidentType.DoesNotExist as e:
            logger.error(f'[ERROR] IncidentType does not exist: {e}')
            return

        core_v1_api, _, _ = get_k8s_apis()
        cameras = await sync_to_async(list)(Camera.objects.all())

        async with aiohttp.ClientSession() as session:
            tasks = []
            for camera in cameras:
                secret_name = f"camera-secret-{camera.id}"
                namespace = 'default'
                login, password = get_secrets(core_v1_api, secret_name, namespace)
                if not login or not password:
                    logger.error(f'[ERROR] Failed to retrieve secrets for camera {camera.id}. Skipping...')
                    continue
                tasks.append(self.check_camera(session, camera, login, password))
            await asyncio.gather(*tasks)

        logger.info('[INFO] Camera status check completed.')

    def handle(self, *args, **kwargs):
        asyncio.run(self.run_checks())