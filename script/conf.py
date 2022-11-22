import os
import yact
import yaml
from flask import Config, jsonify, request
import psycopg2
import pandas as pd
import socket
import logging

class YactConfig(Config):
    def from_yaml(self, config_file, directory=None):
        config = yact.from_file(config_file, directory=directory)
        for section in config.sections:
            self[section.upper()] = config[section]

# fonction configuration
def configuration():
    with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
        cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)
        return cfg

# fonction add_headers
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    return response

#fonction error
def error(message):
    return jsonify({
        'success': False,
        'message': message
    })

# fonction de connection à la BDD
def connect():
    return psycopg2.connect(database=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)

# Fonction de recupération de l'adresse IP
def get_ip_address():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return ip_address

# Fonction Log app
def log_app(message):
    file_formatter = logging.Formatter(
        "{'time':'%(asctime)s', 'service.name': 'Diag_Distant', 'level': '%(levelname)s', 'message': " + str(
            message) + "}"
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    console.setFormatter(file_formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    # logging.basicConfig(format='%(asctime)s %(message)s ' + message, datefmt='%d/%m/%Y %H:%M:%S')
    # logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)



# fonction pour les requetes de type select sans arguments
def select_query(query):
    con = None
    try:
        con = connect()
        df = pd.read_sql(query, con)
        data = df.to_dict(orient='records')
        con.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return data

def truncate_query(query):
    con = connect()
    cursor = con.cursor()
    cursor.execute(query)
    con.commit()

def select_query_argument(query, numero=None):
    con = None
    #numero = request.args.get('numero')
    #where_clause = f'{str(argument)}'
    if numero is not None or numero == "":
        try:
            con = connect()
            df = pd.read_sql(query.format(numero), con)
            data = df.to_dict(orient='records')
            con.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()
        return data
    else:
        return {"message": "la fonction manque un argument : numero"}

# fonction select avec plusieurs arguments
def select_query_date_between(query, arg1=None, arg2=None, arg3=None):
    #data = None
    if arg1 is not None or arg1 == "" or arg2 is not None or arg2 == "" or arg3 is not None or arg3 == "":
        try:
            #duree = arg2 - arg1
            con = connect()
            df = pd.read_sql(query.format(arg1, arg2, arg3), con)
            data = df.to_dict(orient='records')
            con.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()
        return data
    else:
        return {"Error": "Verifier les arguments entrées !!!"}


NAME_DB = configuration()["NAME_DB"]
USER_DB = configuration()["USER_DB"]
PASSWORD_DB = configuration()["PASSWORD_DB"]
HOST_DB = configuration()["HOST_DB"]
PORT_DB = configuration()["PORT_DB"]
