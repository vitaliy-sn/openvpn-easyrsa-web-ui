import textwrap
import datetime
import socket
import os
import re
import json
from envs import *
from system import *

def check_user_exists(user):
    for user_info in list_of_users_from_index_txt():
        if user_info['distinguished_name'].split("=")[1] == user:
            return(True)
    return(False)

def date_to_human_readable(t):
    return(datetime.datetime.strptime(t, '%y%m%d%H%M%SZ').strftime('%Y-%m-%d %H:%M:%S UTC'))
    # return((datetime.datetime.strptime(t, '%y%m%d%H%M%SZ') + datetime.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'))

def render_index_txt(data):
    index_txt = ""
    for n in data:
        if n['flag'] == 'V':
            index_txt += "%s\t%s\t\t%s\t%s\t%s\n" % (n['flag'], n['expiration_date'], n['serial_number'], n['filename'], n['distinguished_name'])
        elif n['flag'] == 'R':
            index_txt += "%s\t%s\t%s\t%s\t%s\t%s\n" % (n['flag'], n['expiration_date'], n['revocation_date'], n['serial_number'], n['filename'], n['distinguished_name'])
    return(index_txt)

# https://community.openvpn.net/openvpn/ticket/623
def mode_crl_fix():
    run_cmd('chmod 755 %s/pki' % easyrsa_path)
    run_cmd('chmod 644 %s/pki/crl.pem' % easyrsa_path)

def list_of_users_from_index_txt():
    index_txt = read_file('%s/pki/index.txt' % easyrsa_path)
    out = []
    for string in index_txt.splitlines():
        if string.startswith('V'):
            flag, expiration_date, serial_number, filename, distinguished_name = string.split()
            if distinguished_name == '/CN=server':
                continue
            out.append({'flag': flag, 'expiration_date': expiration_date, 'serial_number': serial_number, 'filename': filename, 'distinguished_name': distinguished_name})
        elif string.startswith('R'):
            flag, expiration_date, revocation_date, serial_number, filename, distinguished_name = string.split()
            if distinguished_name == '/CN=server':
                continue
            out.append({'flag': flag, 'expiration_date': expiration_date, 'revocation_date': revocation_date, 'serial_number': serial_number, 'filename': filename, 'distinguished_name': distinguished_name})
        # elif string.startswith('E'):
    return(out)

def list_of_users_from_index_txt_human_readable():
    users = list_of_users_from_index_txt()
    for u in users:
        if 'expiration_date' in u.keys():
            u['expiration_date'] = date_to_human_readable(u['expiration_date'])
        if 'revocation_date' in u.keys():
            u['revocation_date'] = date_to_human_readable(u['revocation_date'])
    return(users)

def list_of_users_from_index_txt_human_readable_with_status():
    users = list_of_users_from_index_txt_human_readable()
    current_status = active_clients()
    for u in users:
        try:
            if u['distinguished_name'].split("=")[1] in current_status.keys():
                u['connection_status'] = 'background-color: rgba(232, 245, 233, 0.5);'
            else:
                u['connection_status'] = ''
        except:
            u['connection_status'] = ''
    return(users)

def user_create(user):
    if bool(re.match("^([_a-zA-Z0-9\.-])+$", user)) == False:
        return('You can use only [_a-zA-Z0-9\.-]')
    if check_user_exists(user):
        return('User %s already exists' % user)
    else:
        run_cmd('cd %s && ./easyrsa build-client-full %s nopass' % (easyrsa_path, user))
        return('User %s created' % user)

def user_revoke(user):
    if user.startswith('/CN='):
        user = user.split("=")[1]
    if check_user_exists(user):
        run_cmd('date && cd %s && echo yes | ./easyrsa revoke %s && ./easyrsa gen-crl' % (easyrsa_path, user))
        mode_crl_fix()
        user_connection_reset(user)
        return('User certificate CN=%s revoked' % user)
    else:
        return('User not found')

def user_unrevoke(user):
    if user.startswith('/CN='):
        user = user.split("=")[1]
    if check_user_exists(user):
        users = list_of_users_from_index_txt()
        for i in range(0, len(users), 1):
            if users[i]['distinguished_name'].split("=")[1] == user:
                if users[i]['flag'] == "R":
                    users[i]['flag'] = 'V'
                    users[i].pop('revocation_date', None)
                    write_file('%s/pki/index.txt' % easyrsa_path, render_index_txt(users))
                    run_cmd('cd %s && ./easyrsa gen-crl' % easyrsa_path)
                    mode_crl_fix()
                    return('Certificate CN=%s revocation canceled' % user)
                else:
                    return('User certificate CN=%s not revoked' % user)
    else:
        return('User %s not found' % user)

def render_openvpn_client_config(user):
    config = textwrap.dedent('''\
    remote %s %s tcp
    verb 4
    client
    nobind
    dev tun
    cipher AES-128-CBC
    key-direction 1
    #redirect-gateway def1
    tls-client
    remote-cert-tls server
    # for update resolv.conf on ubuntu
    #script-security 2 system
    #up /etc/openvpn/update-resolv-conf
    #down /etc/openvpn/update-resolv-conf
    ''' % (external_host, external_port))
    config += "<cert>\n%s</cert>\n" % str(read_file('%s/pki/issued/%s.crt' % (easyrsa_path, user)))
    config += "<key>\n%s</key>\n" % str(read_file('%s/pki/private/%s.key' % (easyrsa_path, user)))
    config += "<ca>\n%s</ca>\n" % str(read_file('%s/pki/ca.crt' % easyrsa_path))
    config += "<tls-auth>\n%s</tls-auth>\n" % str(read_file('%s/pki/ta.key' % easyrsa_path))
    return(config)

def user_showcfg(user):
    if user.startswith('/CN='):
        user = user.split("=")[1]
    if check_user_exists(user):
        return(render_openvpn_client_config(user))
    else:
        return('User %s not found' % user)

def user_connection_reset(user):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((management_host, int(management_port)))
        s.recv(65535)
        s.sendall(b"kill %b\n" % bytes(user, 'utf-8'))
        print(str(s.recv(65535), 'utf-8'))
    except:
        print('oops')

def parse_openvpn_client_list(status):
    clients = {}
    flag = False
    for line in status.splitlines():
        if line.startswith('Common Name'):
            flag = True
            continue
        if line.startswith('ROUTING TABLE'):
            return(clients)
        if flag:
            common_name, real_ip, bytes_received, bytes_sent, connected_since = line.split(',')
            clients[common_name] = { 'common_name': common_name, 'real_ip': real_ip,
                                     'bytes_received': bytes_received, 'bytes_sent': bytes_sent,
                                     'connected_since': connected_since }

def active_clients():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((management_host, int(management_port)))
        s.recv(65535)
        s.sendall(b"status\n")
        return(parse_openvpn_client_list(str(s.recv(65535), 'utf-8')))
    except:
        print('oops')
