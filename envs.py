import os

# without / at the end
easyrsa_path = 'easyrsa'

external_host = '192.0.2.42'
external_port = '1194'

management_host = '127.0.0.1'
management_port = '8989'

if os.environ.get('EASYRSA_PATH') is not None:
    easyrsa_path = os.environ.get('EASYRSA_PATH')

if os.environ.get('EXTERNAL_HOST') is not None:
    external_host = os.environ.get('EXTERNAL_HOST')
elif os.environ.get('KUBERNETES_SERVICE_HOST') is not None:
    from kubernetes import *
    external_host = get_service_external_host()

if os.environ.get('EXTERNAL_PORT') is not None:
    external_port = os.environ.get('EXTERNAL_PORT')

if os.environ.get('MANAGEMENT_HOST') is not None:
    external_port = os.environ.get('MANAGEMENT_HOST')

if os.environ.get('MANAGEMENT_PORT') is not None:
    external_port = os.environ.get('MANAGEMENT_PORT')
