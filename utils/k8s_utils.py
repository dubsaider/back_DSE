from kubernetes import client, config
from back.settings import K8S_DOMAIN

def initialize_k8s_api():
    user_cert_file = 'user.crt' 
    user_key_file = 'user.key' 
    ca_cert_file = 'ca.crt' 
    api_server_url = f'https://{K8S_DOMAIN}:6443' 

    configuration = client.Configuration()
    configuration.host = api_server_url
    configuration.verify_ssl = True
    configuration.ssl_ca_cert = ca_cert_file
    configuration.cert_file = user_cert_file
    configuration.key_file = user_key_file
    
    return client.CoreV1Api(client.ApiClient(configuration))