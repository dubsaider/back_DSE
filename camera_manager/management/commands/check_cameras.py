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
        """Получение типа инцидента в зависимости от статуса камеры."""
        return (
            IncidentType.objects.get(name='Изменение статуса камеры на "Активный"')
            if is_active
            else IncidentType.objects.get(name='Изменение статуса камеры на "Неактивный"')
        )

    async def check_camera(self, session, obj, username, password):
        """Проверка доступности камеры с механизмом устойчивости."""
        ip = obj.camera_ip
        current_status = obj.is_active
        consecutive_failures = 0
        new_status = None

        logger.info(f'[INFO] Checking camera with IP: {ip}')

        if ip == '0.0.0.0':
            logger.warning(f'[WARNING] Camera {ip} has an invalid IP address. Marking as inactive.')
            new_status = False
        else:
            try:
                auth = aiohttp.BasicAuth(login=username, password=password)
                async with session.get(f"http://{ip}:554", timeout=5, auth=auth) as response:
                    if response.status == 200:
                        logger.info(f'[INFO] Camera {ip} is reachable and active.')
                        new_status = True
                        consecutive_failures = 0
                    else:
                        logger.warning(f'[WARNING] Camera {ip} is unreachable (HTTP status: {response.status}).')
                        consecutive_failures += 1
                        new_status = False if consecutive_failures >= 3 else current_status
            except asyncio.TimeoutError:
                logger.error(f'[ERROR] Camera check timed out for IP: {ip}')
                consecutive_failures += 1
                new_status = False if consecutive_failures >= 3 else current_status
            except aiohttp.ClientConnectionError:
                logger.error(f'[ERROR] Failed to connect to camera with IP: {ip}')
                consecutive_failures += 1
                new_status = False if consecutive_failures >= 3 else current_status
            except aiohttp.ClientResponseError as e:
                if e.status == 401:
                    logger.warning(f'[WARNING] Camera {ip} requires authorization.')
                    consecutive_failures = 0
                    new_status = True
                else:
                    logger.error(f'[ERROR] Camera check failed for IP: {ip} (HTTP error: {e.status})')
                    consecutive_failures += 1
                    new_status = False if consecutive_failures >= 3 else current_status

        await self.update_camera_status(obj, ip, current_status, new_status)

    async def update_camera_status(self, camera, ip, old_status, new_status):
        """Обновление статуса камеры в базе данных и создание инцидента при необходимости."""
        if old_status != new_status:
            incident_type = self.incident_type_active if new_status else self.incident_type_inactive
            new_incident = Incident(
                camera=camera,
                incident_type=incident_type,
                link=""
            )
            await sync_to_async(new_incident.save)()
            logger.info(f'[INFO] Camera {ip} status changed from {"Active" if old_status else "Inactive"} '
                        f'to {"Active" if new_status else "Inactive"}. Incident created.')
            await sync_to_async(Camera.objects.filter(pk=camera.pk).update)(is_active=new_status)
            logger.info(f'[INFO] Camera {ip} status updated in the database to {"Active" if new_status else "Inactive"}.')
        else:
            logger.info(f'[INFO] Camera {ip} status remains {"Active" if old_status else "Inactive"}.')

    async def run_checks(self):
        """Основная функция для запуска проверки камер."""
        logger.info('[INFO] Starting camera status checks...')

        try:
            self.incident_type_active = await sync_to_async(self.get_incident_type)(True)
            self.incident_type_inactive = await sync_to_async(self.get_incident_type)(False)
        except IncidentType.DoesNotExist as e:
            logger.error(f'[ERROR] IncidentType does not exist: {e}')
            return

        core_v1_api, _, _ = get_k8s_apis()
        cameras = await sync_to_async(list)(Camera.objects.all())

        if not cameras:
            logger.warning('[WARNING] No cameras found in the database.')
            return

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

            logger.info(f'[INFO] Running checks for {len(tasks)} cameras...')
            await asyncio.gather(*tasks)

        logger.info('[INFO] Camera status checks completed successfully.')

    def handle(self, *args, **kwargs):
        """Точка входа для команды Django."""
        asyncio.run(self.run_checks())