from django.core.management.base import BaseCommand
from kubernetes import client
from utils.k8s_utils import initialize_k8s_api
import logging
import asyncio

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Delete Kubernetes resources by name'

    def add_arguments(self, parser):
        parser.add_argument('resource_type', type=str, help='Type of the resource (Deployment, Service, Pod)')
        parser.add_argument('resource_name', type=str, help='Name of the resource')

    def handle(self, *args, **kwargs):
        resource_type = kwargs['resource_type']
        resource_name = kwargs['resource_name']
        k8s_api = initialize_k8s_api()

        if resource_type == 'Deployment':
            asyncio.run(self.delete_deployment(k8s_api, resource_name))
        elif resource_type == 'Service':
            asyncio.run(self.delete_service(k8s_api, resource_name))
        elif resource_type == 'Pod':
            asyncio.run(self.delete_pod(k8s_api, resource_name))
        else:
            logger.error(f"Unsupported resource type: {resource_type}")

        self.stdout.write(self.style.SUCCESS('Successfully deleted Kubernetes resource'))
        logger.info('Kubernetes resource deletion completed.')

    async def delete_deployment(self, k8s_api, deployment_name):
        try:
            await asyncio.to_thread(k8s_api.delete_namespaced_deployment, name=deployment_name, namespace='default')
            logger.info(f"Deployment {deployment_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to delete deployment: {e}")

    async def delete_service(self, k8s_api, service_name):
        try:
            await asyncio.to_thread(k8s_api.delete_namespaced_service, name=service_name, namespace='default')
            logger.info(f"Service {service_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to delete service: {e}")

    async def delete_pod(self, k8s_api, pod_name):
        try:
            await asyncio.to_thread(k8s_api.delete_namespaced_pod, name=pod_name, namespace='default')
            logger.info(f"Pod {pod_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to delete pod: {e}")