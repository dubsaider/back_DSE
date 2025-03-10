from django.core.management.base import BaseCommand
from camera_manager.models import Camera
from kubernetes import client
from back.settings import K8S_ADDRESS, USER_CERT_FILE, USER_KEY_FILE, CA_CERT_FILE

class Command(BaseCommand):
    help = 'Create Kubernetes Secrets for all cameras in the database'

    def handle(self, *args, **kwargs):
        user_cert_file = USER_CERT_FILE
        user_key_file = USER_KEY_FILE
        ca_cert_file = CA_CERT_FILE
        api_server_url = f'https://{K8S_ADDRESS}:6443' # change url

        configuration = client.Configuration()
        configuration.host = api_server_url
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = ca_cert_file
        configuration.cert_file = user_cert_file
        configuration.key_file = user_key_file

        k8s_api = client.CoreV1Api(client.ApiClient(configuration))

        cameras = Camera.objects.all()

        for camera in cameras:
            secret_name = f"camera-secret-{camera.id}"
            secret_data = {
                "camera_name": camera.camera_name,
                "camera_ip": camera.camera_ip,
                "username": "username", # change login
                "password": "password" # change password
            }

            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=secret_name),
                string_data=secret_data
            )

            try:
                k8s_api.create_namespaced_secret(namespace="default", body=secret)
                self.stdout.write(self.style.SUCCESS(f"Successfully created secret {secret_name}"))
            except client.exceptions.ApiException as e:
                self.stdout.write(self.style.ERROR(f"Failed to create secret {secret_name}: {e}"))