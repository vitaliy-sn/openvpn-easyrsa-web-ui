import os

# without / at the end
easyrsa_path = 'easyrsa'

external_ip = '127.127.127.127'
external_port = '1194'

management_host = '127.0.0.1'
management_port = '8989'

if os.environ.get('EASYRSA_PATH') is not None:
    easyrsa_path = os.environ.get('EASYRSA_PATH')

if os.environ.get('EXTERNAL_IP') is not None:
    external_ip = os.environ.get('EXTERNAL_IP')

if os.environ.get('EXTERNAL_PORT') is not None:
    external_port = os.environ.get('EXTERNAL_PORT')

if os.environ.get('MANAGEMENT_HOST') is not None:
    external_port = os.environ.get('MANAGEMENT_HOST')

if os.environ.get('MANAGEMENT_PORT') is not None:
    external_port = os.environ.get('MANAGEMENT_PORT')
