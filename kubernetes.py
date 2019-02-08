import os
import json
import ssl
import http.client
from system import read_file

kube_api_server_host = os.environ.get('KUBERNETES_SERVICE_HOST')
kube_api_server_port = os.environ.get('KUBERNETES_SERVICE_PORT')
kube_current_namespace = os.environ.get('POD_NAMESPACE')
kube_openvpn_external_service_name = 'openvpn-external'

token = read_file('/var/run/secrets/kubernetes.io/serviceaccount/token')

headers = {"Authorization": "Bearer %s" % token}

def kube_api_get(url='/api'):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    conn = http.client.HTTPSConnection(kube_api_server_host, context=context)
    conn.request('GET', url, headers=headers)
    response = conn.getresponse()
    data = str(response.read(), 'utf-8')
    conn.close()
    return(data)

def get_service_external_host():
    try:
        response = json.loads(kube_api_get('/api/v1/namespaces/%s/services/%s' % (kube_current_namespace, kube_openvpn_external_service_name)))
        if 'externalIPs' in response['spec'].keys():
            return(response['spec']['externalIPs'][0])
        elif 'ingress' in response['status']['loadBalancer'].keys():
            if 'hostname' in response['status']['loadBalancer']['ingress'][0]:
                return(response['status']['loadBalancer']['ingress'][0]['hostname'])
            elif 'ip' in response['status']['loadBalancer']['ingress'][0]:
                return(response['status']['loadBalancer']['ingress'][0]['ip'])
    except:
        print('get_service_external_host error')
