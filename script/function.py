import os
from flask import request
import jwt
import yaml
import logging

from http import HTTPStatus
import socket
from psycopg2 import Error
import psycopg2
import pandas as pd
from script.conf import connect

# import request

with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
    cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)


# function de connection à la BDD


# function de decodage du token avec JWT


def decodeToken(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {"data": decoded, 'code': HTTPStatus.OK}
    except:
        return {"message": "invalid token ", 'code': HTTPStatus.UNAUTHORIZED}


# function getRoleToken pour l'attribution des roles
# function getRoleToken pour l'attribution des roles


def getRoleToken(token):
    try:
        roles = decodeToken(token)['data']['realm_access']['roles']
        for role in roles:
            if (role != 'offline_access' and role != 'default-roles-saytu_realm' and role != 'uma_authorization'):
                return role

    except ValueError:
        return {'status': 'Error', 'error': ValueError}


# La fonction getIpAdress()


def getIpAdress():
    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)
    return IP_addres


# La fonction log_app()


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


# La fonction getAllDoublon


def getAllDoublon():
    con = connect()
    query = ''' 
                    Select db.service_id, db.nom_olt, db.ip_olt, db.vendeur, db.created_at::date , mt.oltrxpwr, mt.ontrxpwr
                    From doublons_ftth as db, metric_seytu_network as mt
                    where db.service_id = mt.numero
                    and db.ip_olt = mt.olt_ip order by db.created_at::date desc
                     
            '''
    data_ = pd.read_sql(query, con)
    print(data_)
    res = data_.to_dict(orient='records')
    return res


# La fonction affichage des dernieres heure de coupure


def getDerniereHeureDeCoupure():
    con = connect()
    query = ''' Select numero,nom_olt, ip, vendeur, anomalie, criticite, Max(created_at) as created_at  
                from maintenance_predictive_ftth Group by numero,nom_olt, ip, vendeur, anomalie, criticite
            '''
    data_ = pd.read_sql(query, con)
    print(data_)
    res = data_.to_dict(orient='records')
    return res


# Creation de la table history ftth


def create_table_inventaire_history():
    con = connect()
    cursor = con.cursor()
    try:
        create_table_query = ''' CREATE TABLE IF NOT EXISTS inventaireglobalhistory_ftth 
                     (
                        id serial PRIMARY KEY,
                        pon int NOT NULL, 
                        slot int NOT NULL,
                        nom_olt varchar(100) NOT NULL,
                        nombre_de_numero int NOT NULL,
                        created_at TIMESTAMP DEFAULT Now()
                     ); '''

        cursor.execute(create_table_query)
        con.commit()
        print(" Table create_table_inventaire_history successfully in PostgreSQL ")
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if con:
            cursor.close()
            con.close()


def create_table_debit_history():
    con = connect()
    cursor = con.cursor()
    try:
        create_table_query = ''' CREATE TABLE IF NOT EXISTS inventaireglobal_network_history 
                     (
                        debit_index serial PRIMARY KEY,
                        service_id varchar(100) NOT NULL, 
                        offre varchar(100) NOT NULL, 
                        debit_up int NOT NULL,
                        debit_down int NOT NULL,
                        ip_olt varchar(100) NOT NULL,
                        nom_olt varchar(100) NOT NULL,
                        slot int NOT NULL,
                        pon int NOT NULL,
                        created_at TIMESTAMP DEFAULT Now()
                     ); '''

        cursor.execute(create_table_query)
        con.commit()
        print(" Table create_table_inventaire_history successfully in PostgreSQL ")
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if con:
            cursor.close()
            con.close()


# la fonction data_inventaire


def data_inventaire(numero):
    cnx = connect()
    df = pd.read_sql_query(
        '''SELECT ont_index, ont_id, service_id, ip_olt, slot, pon, pon_index, vendeur, nom_olt FROM inventaireglobal_ftth WHERE service_id = '{}' '''.format(
            numero), con=cnx)
    df = df.set_axis(
        ['ont_index', 'ont_id', 'serviceId', 'ip_olt', 'slot', 'pon', 'ponIndex', 'vendeur', 'nomOlt'], axis=1,
        inplace=False
    )
    return df


# la fonction data_infos_huawei_conf
def data_infos_huawei_conf(ip, pon, slot):
    cnx = connect()
    df = pd.read_sql_query(
        '''SELECT ip, index, onu_id, pon, slot, shelf, vlan, nom_traf_down, nom_traf_up FROM infos_huawei_conf_ftth WHERE ip = '{}' AND pon = '{}' AND slot = '{}' '''.format(
            ip, pon, slot
        ), con=cnx)

    df = df.set_axis(
        ['ip', 'index', 'onuId', 'pon', 'slot', 'shelf', 'vlan', 'nomTrafDown', 'nomTrafUp'], axis=1, inplace=False
    )
    return df


def testQuery():
    cnx = connect()
    df = pd.read_sql_query(''' Select * from inventaireglobal_ftth limit 10 ''', con=cnx)
    print(df)
    res = df.to_dict(orient='records')
    return res
    # return df


def testHistory():
    cnx = connect()
    numero = request.args.get('numero')
    if numero is not None and numero != "":

        # TODO : mettre les restrictions
        df = pd.read_sql_query(''' select Distinct service_id, offre, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
    from inventaireglobal_network_bis where service_id = '{}' '''.format(numero), con=cnx)
        print(df)
        res = df.to_dict(orient='records')
        return res

    else:
        res = testHistoryDefault()
        return res


def testHistoryDefault():
    cnx = connect()
    query = ''' select Distinct service_id, offre, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
from inventaireglobal_network_bis '''
    df_ = pd.read_sql(query, cnx)
    ret_ = df_.to_dict(orient='records')
    return ret_


def testGit():
    name = cfg['NAME_DB']
    return f"vous etes connecté à la base {name}"
