import pandas as pd
from flask import Flask, request, jsonify
from http import HTTPStatus
from script.function import getDerniereHeureDeCoupure, decodeToken, getRoleToken
import os
from script.conf import add_headers, truncate_query, connect, get_ip_address, log_app
from script.main_function import get_historique_coupure_six_mois, get_historique_coupure_date_between, monitoring, create_table, get_doublon, get_coupure, get_historique_coupure, taux_utilisation_debit, \
    metric_date_between, resultat_diagnostic, recherche_elargie, derniere_heure_coupure
from script.account import configuration, admin_token, get_token, get_token_user_admin
import requests
import flask
from flask_cors import CORS
import warnings

warnings.filterwarnings("ignore")  # Ignorer les warnings
app = Flask(__name__)
CORS(app)

# Recuperation des variables
# TODO : doit inclure le host et le port


CLIENT_ID = configuration('CLIENT_ID')
CLIENT_SECRET = configuration('CLIENT_SECRET')
GRANT_TYPE = configuration('GRANT_TYPE')
URI = configuration('URI')
URI_USER = configuration('URI_USER')
URI_ROLES = configuration('URI_ROLES')
REALM = configuration('REALM')
URI_BASE = configuration('URI_BASE')

@app.route('/')
def test_serveur():  # put application's code here
    con = connect()
    if con == None:
        return "Erreur de serveur"
    else:
        return  "Serveur OK..."
    #return 'WELCOME TO Saytu Network Backend Ceci est un Test'

# Good doublons
@app.route('/listedoublons', methods=['GET'])
def get_doublon_api():
    return get_doublon()


# Liste des coupures
@app.route('/listecoupures', methods=['GET'])
def get_coupure_api():
    return get_coupure()


# Historique Taux d'utilisation du débit
@app.route('/historiquetauxutilisation', methods=['GET'])
def taux_utilisation_debit_api():
    return taux_utilisation_debit()


# Historique des coupures
@app.route('/historiquecoupures', methods=['GET'])
def get_historique_coupure_api():
    return get_historique_coupure()

# API permettant de donner l'historique des coupures entres deux dates
@app.route('/historique_coupures_dates', methods=['GET'])
def get_historique_coupure_date_between_api():
    return get_historique_coupure_date_between()

# API permettant d'obtenir l'historique des coupures de 6 mois
@app.route('/historique_coupures_six_mois', methods=['GET'])
def get_historique_coupure_six_mois_api():
    return get_historique_coupure_six_mois()

# API pemettant de faire le diagnostic à temps réels
@app.route('/diagnosticnumero', methods=['GET'])
def monitoring_api():
    return monitoring()


# API permettant d'afficher le resultats du diagnostic
@app.route('/resultatdiagnostic', methods=['GET'])
def resultat_diagnostic_api():
    return resultat_diagnostic()


# API permettant d'afficher la recherche élargie
@app.route('/rechercheelargie', methods=['GET'])
def recherche_elargie_api():
    return recherche_elargie()


# API pour obtenir les metrics d'une ligne entre 2 dates
@app.route('/metric', methods=['GET'])
def metric_date_between_api():
    return metric_date_between()


# API pour l'affichage de la dernière date de coupure
@app.route('/derniereheurecoupure', methods=['GET'])
def derniere_heure_coupure_api():
    return derniere_heure_coupure()

def get_keycloak_headers():
    donnee = get_token_user_admin()
    token_admin = donnee['tokens']['access_token']
    return {
        'Authorization': 'Bearer ' + token_admin,
        'Content-Type': 'application/json'
    }

@app.route('/auth', methods=['POST'])
def get_token_api():
    return get_token()

# Test de la fonction d'activation
@app.route('/users/testActivation/<string:userId>/', methods=['GET'])
def testActivation(userId):
    try:
        headers = flask.request.headers
        reponse = get_user_by_id(userId)
        if reponse.get("status") == 'error':
            return {'message': 'Utilisateur Not Found', 'code': HTTPStatus.NOT_FOUND}
        else:
            return {'message': 'Good User', 'code': 200}
        # headerss = flask.request.headers
        # print("------------------------------Le headerrs est-----------------------")
        # print(headerss)
        # return jsonify({"test": headerss})#print(headers)
    except:
        print("------------------------------Mauvais  Headers------------------")

# Test Get User By ID
@app.route('/testGetUserId', methods=['GET'])
def testGetUserId():
    try:
        userId = '64b43eff-fcdf-4394-b207-0f067afd7894'
        url = URI_USER + '/' + userId
        print("----------------le url recuperer est-------------------")
        print(url)
        donnee = admin_token()
        token_admin = donnee['tokens']['access_token']
        print("---------------le token admin est-----------------")
        print(token_admin)
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        status = response.status_code
        tokens_data = response.json()

        # print(data)
        # data = {lllououoooukykykykyky
        #     "enabled": tokens_data['enabled'],
        #     "id": tokens_data['id'],
        # }
        # print("---")
        return {'message': 'good', 'code': 200, 'status status': status, 'token': token_admin}
        # return {'code':0}
    except:
        print("-----------ERRORR------------------")


# Fonction de test d'activaton
@app.route('/users/activation/', methods=['GET'])
def activation_users():
    try:
        headers = flask.request.headers
        response = get_user_by_id('64b43eff-fcdf-4394-b207-0f067afd7894')
        # if response.get("status") == 'error':
        #     return {"message": "l'utilisateur n'est pas trouve", 'code': HTTPStatus.NOT_FOUND}
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {'message': 'token invalid 1'}
            else:
                return {'message': 'token invalid 2'}
        else:
            return {'message': 'token invalid 3'}

    except:
        print("-------------ERRORR--------")
        return {"Good": "response"}

# Fonction permettant de tester l'obtention du token Admin
@app.route('/testGetTokenUserSimple', methods=['GET'])
def testGetTokenUserSimple():
    url = "https://keycloak-pprod.orange-sonatel.com/auth/realms/Saytu_realm/protocol/openid-connect/token"
    params = {
        'client_id': 'saytu_keycloak_python',
        'grant_type': 'password',
        'client_secret': '5b00ff07-a482-417d-8aff-0e5d83045078',
        'username': 'aziz',
        'password': 'test'
    }
    x = requests.post(url, params, verify=False)
    print(x)
    return jsonify({'message': 'ok', "token": x.json()})


# Fonction de test du get user by ID
@app.route('/testGetUserByID', methods=['GET'])
def GetUserByID(userId):
    try:

        URI_USER = 'https://keycloak-pprod.orange-sonatel.com/auth/admin/realms/saytu_realm/users'
        # userId = '97a28af5-89ad-445b-87e6-4e83afcab8fe'
        # userId = '64b43eff-fcdf-4394-b207-0f067afd7894'
        # userName = 'aziz'
        url = URI_USER + '/' + userId
        # urls = URI_USER + '?username=' + userName
        print('-----------------------le url recuperer est----------------')
        print(url)
        donnee = get_token_user_admin()
        print('-----------------------le url avec userName recuperer est----------------')
        # print(urls)
        donnee = get_token_user_admin()
        token_admin = donnee['tokens']['access_token']
        print('---------------le token Admin recuperer est ---------')
        print(token_admin)
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        # if response.status_code > 200:
        #     return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
        # tokens_data = response.json()
        status = response.status_code
        if status > 200:
            return {'message': 'Erreur', 'status': 'error', 'code': status}
        tokens_data = response.json()
        print("--------------la reponse renvoye  est-----------")
        print(tokens_data)
        print("---------------le status recuperer---------------")
        print(status)
        data = {
            "enabled": tokens_data['enabled'],
            "id": tokens_data['id'],
            "firstName": tokens_data['firstName'],
            "lastName": tokens_data['lastName'],
            "username": tokens_data['username'],
        }
        response = {'status': 'Success', 'data': data, 'code': HTTPStatus.OK}
        return response
        # return {'message': 'test', 'status': status, 'code': 200}
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})
        # Do Something


# la fonction permettant d'avoir tous les info user
@app.route('/testGetInfoUser', methods=['GET'])
def GetInfoUser(userId):
    try:

        URI_USER = 'https://keycloak-pprod.orange-sonatel.com/auth/admin/realms/saytu_realm/users'
        # userId = '64b43eff-fcdf-4394-b207-0f067afd7894'
        url = URI_USER + '/' + userId + '/role-mappings/realm'
        donnee = get_token_user_admin()
        token_admin = donnee['tokens']['access_token']
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        if response.status_code > 200:
            return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
        tokens_data = response.json()
        data = {
            "name": tokens_data[0]['name'],
            "id": tokens_data[0]['id']

        }
        print("la data recuper est --------------------------------------------------")
        print(data)

        return data
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API pour consulter la liste des utilisateurs
@app.route('/users/', methods=['GET'])
def GetAllUsers():
    try:

        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                    print('--------------------le token retourne est--------------------')
                    print(token)
                    data = {'message': 'token valid', 'token retourne': token}
                    print(data)
                    # return data
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        print('--------------------------la data renvoye est-------------------')
        print(data)
        code = data['code']
        name = data['data']['name']

        if code == 200:
            data = {"code": code, "name": name, "data": data}
            print(data)
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':
                print('-------------le role est ---------------')
                print(getRoleToken(token))

                url = URI_USER + '?max=1000'
                donnee = get_token_user_admin()
                token_admin = donnee['tokens']['access_token']
                response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                result = []
                for i in range(len(tokens_data)):
                    data = {
                        'enabled': tokens_data[i]['enabled'],
                        'id': tokens_data[i]['id'],
                        'firstName': tokens_data[i]['firstName'],
                        'lastName': tokens_data[i]['lastName'],
                        'username': tokens_data[i]['username'],
                        'profil': GetInfoUser(tokens_data[i]['id']),

                    }
                    result.append(data)
                response = jsonify({'status': 'Success', 'data': result, 'code': HTTPStatus.OK})
                messageLogging = name + " a consulté la liste des utilisateurs "
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),

                }
                log_app(message_log)
                return add_headers(response)
            messageLogging = name + "a tenté de consulter la liste des utilisateurs"
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)

            return {'message': 'invalid user', 'code': HTTPStatus.UNAUTHORIZED}
        else:

            return decodeToken(token)

            # return data
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant l'obtention d'un seul user
@app.route('/users/<string:userId>/', methods=['GET'])
def GetOnlyUser(userId):
    try:
        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        donneerec = {'code': code, 'name': name}
        print('-------------------la data recuperer est-------------')
        print(donneerec)
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                url = URI_USER + '/' + userId
                donnee = get_token_user_admin()
                token_admin = donnee['tokens']['access_token']
                response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()

                response = jsonify({'status': 'Success', 'data': tokens_data, 'code': HTTPStatus.OK})
                GetUserByID(userId)

                messageLogging = name + " a consulté l'utilisateur " + GetUserByID(userId)['data']['username']
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)

                return add_headers(response)
            messageLogging = name + " a tenté de consulter l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            return {"message": "invalid user", "code": HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de creer un utitlisateur
@app.route('/users', methods=['POST'])
def CreateUser():
    try:
        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data_token = decodeToken(token)
        code = data_token['code']
        name = data_token['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # ceci est un test : les roles de creation des users doivent etre établis par la matrice de reponsabilite

                url = URI_USER

                body = request.get_json()
                # for field in ['firstName', 'lastName', 'username', 'password']:
                #     if field not in body:
                #         return error(f"Field {field} is missing!"), 400

                data = {
                    "firstName": body['firstName'],
                    "lastName": body['lastName'],
                    "enabled": "true",
                    "username": body['username'],
                    "credentials": [
                        {
                            "type": "password",
                            "value": body['password'],
                            "temporary": False
                        }
                    ]
                }

                # return data

                donnee = get_token_user_admin()
                headers = get_keycloak_headers()
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 409:
                    return {"message": "Le nom de l'utilisateur existe Déjà", 'status': 'error',
                            'code': response.status_code}
                if response.status_code > 201:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify({'status': 'Success', 'data': 'Utilisateur Créé avec succès', 'code': HTTPStatus.OK})
                messageLogging = name + " a cree l'utilisateur " + body['firstName'] + ' ' + body[
                    'lastName'] + '' + ' de username ' + body['username']
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                return add_headers(response)
            # messageLogging = name + " a tenté de creer l'utilisateur " + body['firstName'] + ' ' + body[
            #         'lastName'] + '' + ' de username' + body['username']
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# API permettant de modifier les params d'un utilisateur
@app.route('/users/<string:userId>/', methods=['PUT'])
def UpdateUser(userId):
    try:
        headers = flask.request.headers
        reponse = GetUserByID(userId)
        prenom = reponse.get("data")["firstName"]
        nom = reponse.get("data")["lastName"]
        login = reponse.get("data")["username"]

        if reponse.get("status") == 'error':
            return {"message": "User Not Found", 'code': HTTPStatus.NOT_FOUND}
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data_token = decodeToken(token)
        code = data_token['code']
        name = data_token['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # ceci est un test Ne doit posseder que le role admin
                url = URI_USER + '/' + userId

                body = request.get_json()
                # TODO : les controles doivent etre faites ici : firstName, lastName ...
                data = {
                    "firstName": body['firstName'],
                    "lastName": body['lastName'],
                    # "enabled": body['enabled'],
                    "username": body['username'],

                    "credentials": [
                        {
                            "type": "password",
                            "value": body['password'],
                            "temporary": False
                        }
                    ]
                }

                donnee = get_token_user_admin()
                token_admin = donnee['tokens']["access_token"]
                headers = get_keycloak_headers()
                response = requests.put(url, headers=headers, json=data)
                if response.status_code > 204:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur modifie avec success', 'code': HTTPStatus.OK})
                messageLogging = name + " a modifie l'utilisateur " + prenom + ' ' + nom + '' + ' de username ' + login + " en " + \
                                 body['firstName'] + ' ' + body['lastName'] + '' + ' de username ' + body['username']

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)

                return add_headers(response)
            messageLogging = name + " a tenté de modifier l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)

            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)

    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant d'activer l'utilisateur
@app.route('/users/enable/<string:userId>/', methods=['PUT'])
def EnableDisableUser(userId):
    try:
        headers = flask.request.headers
        reponse = GetUserByID(userId)

        if reponse.get("status") == 'error':
            return {"message": "User Not Found", 'code': HTTPStatus.NOT_FOUND}
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data_token = decodeToken(token)
        code = data_token['code']
        name = data_token['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':  # Le sf est à ommettre , ceci est un test
                url = URI_USER + '/' + userId
                body = request.get_json()

                data = {
                    "enabled": not body['enabled'],
                }

                donnee = get_token_user_admin()
                token_admin = donnee['tokens']["access_token"]
                headers = get_keycloak_headers()
                response = requests.put(url, headers=headers, json=data)

                if response.status_code > 204:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur Activé/Desactivé avec success', 'code': HTTPStatus.OK})
                if not body['enabled'] == True:
                    print('ok')
                    messageLogging = name + " a désactivé l'utilisateur " + GetUserByID(userId)['data']['username']
                else:
                    print('ok')
                    messageLogging = name + " a activé l'utilisateur " + GetUserByID(userId)['data']['username']

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                return add_headers(response)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)



    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de supprimer un utilisateur
@app.route('/users/<string:userId>/', methods=['DELETE'])
def DeleteUser(userId):
    try:
        headers = flask.request.headers
        reponse = GetUserByID(userId)
        if reponse.get("status") == 'error':
            return {"message": "User Not Found", 'code': HTTPStatus.NOT_FOUND}
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data_token = decodeToken(token)
        code = data_token['code']
        name = data_token['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # sf n'est pas autorisé seull admin doit pouvoir faire cette demande

                url = URI_USER + '/' + userId
                donnee = get_token_user_admin()
                token_admin = donnee['tokens']["access_token"]
                headers = get_keycloak_headers()
                messageLogging = name + " a supprimé l'utilisateur " + GetUserByID(userId)['data']['username']
                response = requests.delete(url, headers=headers)

                if response.status_code > 204:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)

                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur supprimé avec success', 'code': HTTPStatus.OK})

                return add_headers(response)
            messageLogging = name + " a tenté de supprimer l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de visualiser les profils des utilisateurs
@app.route('/profils/', methods=['GET'])
def AllProfils():
    try:

        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                url = URI_ROLES
                donnee = get_token_user_admin()
                token_admin = donnee['tokens']["access_token"]
                response = requests.get(url,
                                        headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                # return jsonify(tokens_data)
                # input_dict = json.loads(tokens_data)

                # Filter python objects with list comprehensions
                output_dict = [x for x in tokens_data if
                               x['name'] == 'admin' or x['name'] == 'profil_1' or x[
                                   'name'] == 'profil_3' or x['name'] == 'sf' or x['name'] == 'profil_4']

                # Transform python object back into json
                # output_json = json.dumps(output_dict)

                response = jsonify({'status': 'Success', 'data': output_dict, 'code': HTTPStatus.OK})
                messageLogging = name + " a consulté la liste des profils "
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                return add_headers(response)
            messageLogging = name + " a tenté de consulter la liste des profils "
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# API permettant de creer le profil d'un utilisateur
@app.route('/profils/', methods=['POST'])
def CreateProfils():
    try:

        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                body = request.get_json()
                # TODO : a mettre les restrictions sur name

                data = {
                    "name": body["name"],
                    "composite": False,
                    "clientRole": False,
                    "containerId": "Saytu_realm"
                }
                url = URI_ROLES
                headers = get_keycloak_headers()
                response = requests.post(url, headers=headers, json=data)
                if response.status_code > 201:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                # return jsonify(tokens_data)

                response = jsonify({'status': 'Success', 'data': tokens_data, 'code': HTTPStatus.OK})
                messageLogging = name + " a cree le profil suivant " + body["name"]
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                return add_headers(response)
            # messageLogging = name + " a de cree le profil suivant "
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


@app.route('/users/profils/<string:userId>/', methods=['POST'])
def UserRole(userId):
    try:
        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # le role sf est un test ici, seul l'admin a le droit de crer des profils
                body = request.get_json()
                result = {
                    "name": body["name"],
                    # "id": body["id"],
                }
                print('------------ le res renvoye est----------')
                print(result)
                data = [result]
                url = URI_USER + '/' + userId + '/role-mappings/realm'
                headers = get_keycloak_headers()
                # TODO : appele la fonction deleteProfilUser
                DeleteProfilUser(userId)
                response = requests.post(url, headers=headers, json=data)
                if response.status_code > 204:
                    return {"message": "Erreur", 'status': response.json(), 'code': response.status_code}
                response = jsonify({'status': 'Success', 'data': 'Profil attribue avec success', 'code': HTTPStatus.OK})
                messageLogging = name + " a modifie le profil " + body["old_profil"] + " de l'utilisateur " + \
                                 GetUserByID(userId)['data']['username'] + ' en profil ' + body['name']

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": get_ip_address(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                return add_headers(response)

            messageLogging = name + " a tenté de modifier l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)

            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)

    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de se déconnecter
@app.route('/logout/', methods=['GET'])
def logout():
    try:
        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:

            messageLogging = name + " s'est deconnecté "
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": get_ip_address(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            response = jsonify({'status': 'Success', 'data': 'Logout', 'code': HTTPStatus.OK})
            return add_headers(response)
        else:
            return decodeToken(token)

    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# fonction DeleteProfilUser
def DeleteProfilUser(userId):
    url = URI_USER + '/' + userId + '/role-mappings/realm'
    donnee = get_token_user_admin()
    token_admin = donnee['tokens']["access_token"]
    response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
    for role in response.json():
        if (role.get('name') != 'offline_access' and role.get('name') != 'default-roles-saytu_realm' and role.get(
                'name') != 'uma_authorization'):
            result = {
                "name": role.get('name'),
                "id": role.get('id'),
            }

            data = [result]
            url = URI_USER + '/' + userId + '/role-mappings/realm'
            headers = get_keycloak_headers()
            reponse = requests.delete(url, headers=headers, json=data)


# La fonction get_user_by_id
def get_user_by_id(userId):
    try:
        url = URI_USER + '/' + userId
        donnee = admin_token()
        token_admin = donnee['tokens']["access_token"]
        response = requests.get(url,
                                headers={'Authorization': 'Bearer {}'.format(token_admin)})
        if response.status_code > 200:
            return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
        tokens_data = response.json()
        data = {
            "enabled": tokens_data['enabled'],
            "id": tokens_data['id'],
            "firstName": tokens_data['firstName'],
            "lastName": tokens_data['lastName'],
            "username": tokens_data['username'],
        }
        response = {'status': 'Success', 'data': data, 'code': HTTPStatus.OK}
        return response
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# la fonction get_info_user
def get_info_user(userId):
    try:
        url = URI_USER + '/' + userId + '/role-mappings/realm'
        donnee = admin_token()
        token_admin = donnee['tokens']["access_token"]
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        if response.status_code > 200:
            return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
            tokens_data = response.json
            data = {
                "name": tokens_data[0]['name'],
                "id": tokens_data[0]['id']
            }
            return data
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})

#create_table()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

