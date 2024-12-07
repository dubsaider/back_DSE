from kubernetes import client, config
import base64
from back.settings import K8S_ADDRESS
import logging

logger = logging.getLogger(__name__)

def initialize_k8s_api():
    user_cert_file = 'user.crt' 
    user_key_file = 'user.key' 
    ca_cert_file = 'ca.crt' 
    api_server_url = f'https://{K8S_ADDRESS}:6443' 

    configuration = client.Configuration()
    configuration.host = api_server_url
    configuration.verify_ssl = True
    configuration.ssl_ca_cert = ca_cert_file
    configuration.cert_file = user_cert_file
    configuration.key_file = user_key_file
    
    return client.CoreV1Api(client.ApiClient(configuration))

async def get_secrets(k8s_api, secret_name, namespace='default'):
    try:
        secret = k8s_api.read_namespaced_secret(name=secret_name, namespace=namespace)
        login = base64.b64decode(secret.data.get('username')).decode('utf-8')
        password = base64.b64decode(secret.data.get('password')).decode('utf-8')
        return login, password
    except client.exceptions.ApiException as e:
        logger.error(f"[ERROR] Failed to retrieve secret {secret_name}: {e}")
        return None, None