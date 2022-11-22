import requests
from script.conf import configuration
from flask import request, jsonify
import os
from http import HTTPStatus
from script.conf import get_ip_address, log_app

CLIENT_ID = configuration()['CLIENT_ID']
CLIENT_SECRET = configuration()['CLIENT_SECRET']
GRANT_TYPE = configuration()['GRANT_TYPE']
URI = configuration()['URI']
URI_USER = configuration()['URI_USER']
URI_ROLES = configuration()['URI_ROLES']
REALM = configuration()['REALM']
URI_BASE = configuration()['URI_BASE']


# fonction adminToken
def adminToken():
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    url = URI
    response = requests.post(url, data=data)

    if response.status_code > 200:
        return {"message": "Username ou Password Incorrect", 'status': 'error'}
    tokens_data = response.json()
    ret = {
        'tokens': {"access_token": tokens_data['access_token'],
                   "token_type": tokens_data['token_type'],
                   },
        "status": 'success',
    }
    return ret


# Fonction permettant l'authentification avec le token
def get_token():
    # TODO : Control username et password
    body = request.get_json(force=True)

    data = {

        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": 'password',
        'username': body['username'],
        'password': body['password']
    }

    url = URI
    response = requests.post(url, data=data)

    if response.status_code > 200:
        messageLogging = body['username'] + " a tenté de se connecter sans success "
        message_log = {
            "url.path": request.base_url,
            "http.request.method": request.method,
            "client.ip": get_ip_address(),
            "event.message": messageLogging,
            "process.id": os.getpid(),
        }
        log_app(message_log)
        print('-----------------------LOG--------------------')
        print(message_log)

        return {"message": "Username ou Password Incorrect", 'code': HTTPStatus.BAD_REQUEST}

    tokens_data = response.json()

    ret = {
        'tokens': {
            "access_token": tokens_data['access_token'],
            "refresh_token": tokens_data['refresh_token'],
        }
    }

    messageLogging = body['username'] + " s'est connecté avec success"
    message_log = {
        "url.path": request.base_url,
        "http.request.method": request.method,
        "client.ip": get_ip_address(),
        "event.message": messageLogging,
        "process.id": os.getpid(),
    }
    log_app(message_log)

    print('-----------------------LOG--------------------')
    print(message_log)

    return jsonify(ret), 200
