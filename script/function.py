import os
from flask import request
import jwt
import yaml
import logging
from script.conf import select_query_argument
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
        ['ont_index', 'ont_id', 'serviceId', 'ip_olt', 'slot', 'pon', 'ponIndex', 'vendeur', 'nomOlt'],
        axis=1, inplace=False)
    return df

# la fonction get_vendeur permettant d'obtenir le vendeur à partir du serviceId
def get_vendeur(numero):
    #cnx = connect()
    data = select_query_argument(''' Select vendeur from inventaireglobal_ftth where service_id = '{}' ''', numero)
    #print('---------------------------Les donnees recuperes-----------------------------')
    #print(data)
    data_ = ''
    for row in data:
        # print(row['vendeur'])
        data_ = row['vendeur']
        # print(data_)
    #print('---------------recup final------------')
    #print(data_)
    # return data_
    return data_

    # df = pd.read_sql_query(
    #     ''' Select vendeur from inventaireglobal_ftth where service_id = '{}' '''.format(
    #         numero), con=cnx)
    # df = df.set_axis(
    #     ['ont_index', 'ont_id', 'serviceId', 'ip_olt', 'slot', 'pon', 'ponIndex', 'vendeur', 'nomOlt'],
    #     axis=1, inplace=False)
    # return df
# la fonction data_invent
def data_invent():
    cnx = connect()
    df = pd.read_sql_query(
        '''SELECT ont_index, ont_id, service_id, ip_olt, slot, pon, pon_index, vendeur, nom_olt FROM inventaireglobal_ftth ''',
        con=cnx)

    df = df.set_axis(
        ['ont_index', 'ont_id', 'serviceId', 'ip_olt', 'slot', 'pon', 'ponIndex', 'vendeur', 'nomOlt'],
        axis=1, inplace=False)
    return df

# la fonction pathMaintenance
def pathMaintenance():
    return os.path.dirname(os.path.abspath(__file__)) + "/output/maintenances/"

# la fonction data_infos_huawei_conf
def data_infos_huawei_conf(ip, pon, slot):
    cnx = connect()
    df = pd.read_sql_query(
        '''SELECT ip, index, onu_id, pon, slot, shelf, vlan, nom_traf_down,nom_traf_up  FROM infos_huawei_conf_ftth WHERE ip = '{}' AND pon = '{}' AND slot ='{}' '''.format(
            ip, pon, slot),
        con=cnx)

    df = df.set_axis(
        ['ip', 'index', 'onuId', 'pon', 'slot', 'shelf', 'vlan', 'nomTrafDown', 'nomTrafUp'],
        axis=1, inplace=False)
    return df

