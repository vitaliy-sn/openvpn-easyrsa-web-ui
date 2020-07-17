#!/usr/bin/env python3

from flask import Flask, request, make_response
import json

from openpvn import *

app = Flask(__name__, static_url_path='', static_folder='frontend')
app.config['DEBUG'] = True

@app.route('/')
def index():
    return(read_file('frontend/index.html'))

@app.route('/api/v1/users/list')
def route_users_list():
    return(json.dumps(list_of_users_from_index_txt_human_readable_with_status(), indent=4, sort_keys=True))

@app.route('/api/v1/user/create')
def route_user_create():
    return(user_create(request.args.get('user')))

@app.route('/api/v1/user/revoke')
def route_user_revoke():
    return(user_revoke(request.args.get('user')))

@app.route('/api/v1/user/unrevoke')
def route_user_unrevoke():
    return(user_unrevoke(request.args.get('user')))

@app.route('/api/v1/user/showcfg')
def route_user_showcfg():
    return(user_showcfg(request.args.get('user')))

@app.route('/api/v1/user/downloadcfg')
def route_user_downloadcfg():
    user = request.args.get('user')
    filename = user.split('=')[1]
    response = make_response(user_showcfg(user), 200)
    response.headers['Content-Disposition'] = 'attachment;filename={}.ovpn'.format(filename)
    response.headers['Content-Type'] = 'application/octet-stream'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')
