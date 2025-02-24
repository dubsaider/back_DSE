from kubernetes import client, config
import base64
from back.settings import K8S_ADDRESS, USER_CERT_FILE, USER_KEY_FILE, CA_CERT_FILE
import logging


logger = logging.getLogger(__name__)


def get_k8s_apis():
    """Инициализирует все необходимые Kubernetes API."""
    user_cert_file = USER_CERT_FILE
    user_key_file = USER_KEY_FILE
    ca_cert_file = CA_CERT_FILE
    api_server_url = f'https://{K8S_ADDRESS}:6443'

    configuration = client.Configuration()
    configuration.host = api_server_url
    configuration.verify_ssl = True
    configuration.ssl_ca_cert = ca_cert_file
    configuration.cert_file = user_cert_file
    configuration.key_file = user_key_file

    api_client = client.ApiClient(configuration)
    core_v1_api = client.CoreV1Api(api_client)
    apps_v1_api = client.AppsV1Api(api_client)
    networking_api = client.NetworkingV1Api(api_client)

    return core_v1_api, apps_v1_api, networking_api


def get_secrets(core_v1_api, secret_name, namespace='default'):
    """Получает секреты из Kubernetes."""
    try:
        secret = core_v1_api.read_namespaced_secret(name=secret_name, namespace=namespace)
        login = base64.b64decode(secret.data.get('username')).decode('utf-8')
        password = base64.b64decode(secret.data.get('password')).decode('utf-8')
        return login, password
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to retrieve secret {secret_name}: {e}")
        return None


def create_pod(api_instance, pod_manifest, namespace="default"):
    """Создает Pod в указанном namespace."""
    try:
        api_response = api_instance.create_namespaced_pod(
            body=pod_manifest,
            namespace=namespace
        )
        logger.info(f"Pod created: {api_response.metadata.name}")
        return api_response
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to create Pod: {e}")


def create_service(api_instance, service_manifest, namespace="default"):
    """Создает Service в указанном namespace."""
    try:
        api_response = api_instance.create_namespaced_service(
            body=service_manifest,
            namespace=namespace
        )
        logger.info(f"Service created: {api_response.metadata.name}")
        return api_response
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to create Service: {e}")


def create_ingress(networking_api, camera, namespace="default"):
    """
    Создает новый Ingress для указанной камеры.

    :param networking_api: Экземпляр NetworkingV1Api для взаимодействия с API Kubernetes.
    :param camera: Объект камеры, содержащий атрибут `id`.
    :param namespace: Пространство имен Kubernetes (по умолчанию "default").
    :return: Имя созданного Ingress или None в случае ошибки.
    """
    ingress_name = f"go2rtc-camera-{camera.id}-ingress"

    ingress_body = client.V1Ingress(
        api_version="networking.k8s.io/v1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(
            name=ingress_name,
            annotations={
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                "nginx.ingress.kubernetes.io/use-regex": "true"
            }
        ),
        spec=client.V1IngressSpec(
            ingress_class_name="nginx",
            rules=[
                client.V1IngressRule(
                    host="",
                    http=client.V1HTTPIngressRuleValue(
                        paths=[
                            client.V1HTTPIngressPath(
                                path=f"/cameras/go2rtc-{camera.id}(/|$)(.*)",
                                path_type="ImplementationSpecific",
                                backend=client.V1IngressBackend(
                                    service=client.V1IngressServiceBackend(
                                        name=f"go2rtc-{camera.id}-service",
                                        port=client.V1ServiceBackendPort(number=80)
                                    )
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    try:
        networking_api.create_namespaced_ingress(namespace=namespace, body=ingress_body)
        logger.info(f"Created new Ingress for camera {camera.id}: {ingress_name}")
        return ingress_name
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to create Ingress for camera {camera.id}: {e}")
        return None


def delete_pod(api_instance, pod_name, namespace="default"):
    """Удаляет Pod из указанного namespace."""
    try:
        api_instance.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace,
            body=client.V1DeleteOptions(propagation_policy='Foreground', grace_period_seconds=0)
        )
        logger.info(f"Pod deleted: {pod_name}")
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to delete Pod: {e}")


def delete_service(api_instance, service_name, namespace="default"):
    """Удаляет Service из указанного namespace."""
    try:
        api_instance.delete_namespaced_service(
            name=service_name,
            namespace=namespace
        )
        logger.info(f"Service deleted: {service_name}")
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to delete Service: {e}")


def delete_ingress(networking_api, camera, namespace="default"):
    """
    Удаляет Ingress для указанной камеры.

    :param networking_api: Экземпляр NetworkingV1Api для взаимодействия с API Kubernetes.
    :param camera: Объект камеры, содержащий атрибут `id`.
    :param namespace: Пространство имен Kubernetes (по умолчанию "default").
    """
    ingress_name = f"go2rtc-camera-{camera.id}-ingress"

    try:
        networking_api.delete_namespaced_ingress(
            name=ingress_name,
            namespace=namespace
        )
        logger.info(f"Ingress deleted for camera {camera.id}: {ingress_name}")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            logger.warning(f"Ingress {ingress_name} not found (might have been already deleted).")
        else:
            logger.error(f"[ERROR] Failed to delete Ingress for camera {camera.id}: {e}")