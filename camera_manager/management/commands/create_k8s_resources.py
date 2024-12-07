from django.core.management.base import BaseCommand
from kubernetes import client
from utils.k8s_utils import initialize_k8s_api
import logging
import yaml
import asyncio

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create Kubernetes resources from provided manifests'

    def add_arguments(self, parser):
        parser.add_argument('manifest_path', type=str, help='Path to the manifest file')

    def handle(self, *args, **kwargs):
        manifest_path = kwargs['manifest_path']
        k8s_api = initialize_k8s_api()
        manifest = self.load_manifest(manifest_path)

        if manifest['kind'] == 'Deployment':
            asyncio.run(self.create_deployment(k8s_api, manifest))
        elif manifest['kind'] == 'Service':
            asyncio.run(self.create_service(k8s_api, manifest))
        elif manifest['kind'] == 'Pod':
            asyncio.run(self.create_pod(k8s_api, manifest))
        else:
            logger.error(f"Unsupported resource kind: {manifest['kind']}")

        self.stdout.write(self.style.SUCCESS('Successfully created Kubernetes resource'))
        logger.info('Kubernetes resource creation completed.')

    def load_manifest(self, manifest_path):
        with open(manifest_path, 'r') as file:
            return yaml.safe_load(file)

    async def create_deployment(self, k8s_api, deployment_manifest):
        try:
            await asyncio.to_thread(k8s_api.create_namespaced_deployment, namespace='default', body=deployment_manifest)
            logger.info(f"Deployment {deployment_manifest['metadata']['name']} created successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to create deployment: {e}")

    async def create_service(self, k8s_api, service_manifest):
        try:
            await asyncio.to_thread(k8s_api.create_namespaced_service, namespace='default', body=service_manifest)
            logger.info(f"Service {service_manifest['metadata']['name']} created successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to create service: {e}")

    async def create_pod(self, k8s_api, pod_manifest):
        try:
            await asyncio.to_thread(k8s_api.create_namespaced_pod, namespace='default', body=pod_manifest)
            logger.info(f"Pod {pod_manifest['metadata']['name']} created successfully.")
        except client.exceptions.ApiException as e:
            logger.error(f"Failed to create pod: {e}")