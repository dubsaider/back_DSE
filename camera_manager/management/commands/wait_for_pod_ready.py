from django.core.management.base import BaseCommand
from kubernetes import client
from utils.k8s_utils import initialize_k8s_api
import logging
import asyncio

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Wait for a Kubernetes pod to be ready'

    def add_arguments(self, parser):
        parser.add_argument('pod_name', type=str, help='Name of the pod to wait for')

    def handle(self, *args, **kwargs):
        pod_name = kwargs['pod_name']
        k8s_api = initialize_k8s_api()

        asyncio.run(self.wait_for_pod_ready(k8s_api, pod_name))

        self.stdout.write(self.style.SUCCESS(f'Pod {pod_name} is ready'))
        logger.info(f'Pod {pod_name} is ready.')

    async def wait_for_pod_ready(self, k8s_api, pod_name):
        for _ in range(60):
            try:
                pod = await asyncio.to_thread(k8s_api.read_namespaced_pod, name=pod_name, namespace='default')
                if pod.status.phase == 'Running':
                    return
            except client.exceptions.ApiException as e:
                logger.error(f"Failed to read pod {pod_name}: {e}")
            await asyncio.sleep(1)
        raise Exception(f"Pod {pod_name} did not start in time.")