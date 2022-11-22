import psycopg2
from psycopg2 import Error
from script.conf import *
import pandas as pd
from datetime import datetime
from script.function import get_vendeur

from script.confClientsNokia import getProvisioning
from script.confClientsHuawei import configurationClientsHuawei


# import datetime


def simple_inventaire():
    data = select_query(''' SElect * from historique_diagnostic limit 10 ''')
    return data


# fonction doublon
def get_doublon():
    numero = request.args.get('numero')
    if numero is not None:
        data = select_query_argument('''Select db.service_id, db.created_at::date, db.nom_olt, db.ip_olt, db.vendeur, mt.oltrxpwr, mt.ontrxpwr
                                                   From doublons_ftth as db, metric_seytu_network as mt
                                                   where db.service_id = mt.numero 
                                                   and db.ip_olt = mt.olt_ip
                                                   and db.service_id = '{}'  order by db.created_at::date desc''',
                                     numero)
        return data
    else:
        return 'Vous devez saisir un numero'



# Liste des coupures
def get_coupure():
    numero = request.args.get('numero')
    if numero is None or numero == "":
        return "La liste des coupures est vide"
    else:
        data = select_query_argument('''SELECT numero,pon , slot, ip, nom_olt, vendeur, anomalie, criticite,   created_at  
	                                         FROM maintenance_predictive_ftth WHERE anomalie LIKE '%Coupure%' AND numero = '{}' ''',
                                     numero)
        return data


# Historique du taux d'utilisation
def taux_utilisation():
    numero = request.args.get('numero')
    if numero is None or numero == "":
        data = select_query('''SELECT DISTINCT service_id, offre,vendeur, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
                               FROM inventaireglobal_network_bis''')

        df = pd.DataFrame(data)
        i = 0
        for row in df.itertuples():
            # print(row.offre)
            if row.offre == "FIBRE BI":
                debitMoySouscrit = "20 MB"
                # print(row.offre + "::" + debitMoySouscrit)
            elif row.offre == "FIBRE MAX":
                debitMoySouscrit = "40 MB"
                # print(row.offre + "::" + debitMoySouscrit)
            elif row.offre == "FIBRE MEGA":
                debitMoySouscrit = "60 MB"
                # print(row.offre + "::" + debitMoySouscrit)
            else:
                debitMoySouscrit = "100 MB"
                # print(row.offre + "::" + debitMoySouscrit)

            print(row.service_id + "::" + row.offre + "::" + debitMoySouscrit)
            data_ = {"service_id": row.service_id, "offre": row.offre, "DebitMoy": debitMoySouscrit}
            # return datawithdebitsouscrit
            # return data_

        return data
        # return datawithdebitsouscrit
        # return data_
    else:
        data = select_query_argument(''' SELECT DISTINCT service_id, offre, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
                                         FROM inventaireglobal_network_bis where  service_id = '{}' ''', numero)
        return data


# Fonction Historique des coupures sur x jours ou x mois

def get_historique_coupure():
    dateDebut = request.args.get('dateDebut')
    dateFin = request.args.get('dateFin')
    dateDebut = datetime.strptime(dateDebut, '%Y-%m-%d')
    dateFin = datetime.strptime(dateFin, '%Y-%m-%d')
    dateDebut = dateDebut.date()
    dateFin = dateFin.date()
    duree = dateFin - dateDebut
    duree = duree.days

    if dateDebut is not None and dateFin is not None:
        data = select_query_date_between(
            '''Select numero, ip, anomalie, nom_olt,  count(numero) as Dureee
                      FROM maintenance_predictive_ftth
                      WHERE date BETWEEN '{}'  AND  '{}'
                      GROUP BY numero, ip, anomalie, nom_olt
                      HAVING COUNT(numero) = {} ''',
            dateDebut, dateFin, duree)
        return data
    else:
        return "Veuillez saisir les dates"


# la fonction taux d'utilisation avec débit
def taux_utilisation_debit():
    data_ = []
    numero = request.args.get('numero')
    data = select_query_argument(''' SELECT DISTINCT service_id, offre, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
                                         FROM inventaireglobal_network_bis where  service_id = '{}' ''', numero)

    df = pd.DataFrame(data)
    i = 0

    for row in df.itertuples():
        # print(row.debitdown)
        # debitSouscrit = 20
        if row.offre == "FIBRE BI":
            debitSouscrit = 20
        elif row.offre == "FIBRE MAX":
            debitSouscrit = 40
        elif row.offre == "FIBRE MEGA":
            debitSouscrit = 60
        else:
            debitSouscrit = 100
        debitdown = row.debitdown
        taux = (debitdown / debitSouscrit) * 100
        # print(f"\n{taux}")
        dict = {'debitSouscrit': debitSouscrit, 'Taux': taux, 'offre': row.offre, 'debitdown': row.debitdown,
                'debitup': row.debitup, 'ip_olt': row.ip_olt, 'nom_olt': row.nom_olt, 'pon': row.pon,
                'service_id': row.service_id, 'slot': row.slot}
        data_.append(dict)
        df2 = pd.DataFrame(data=dict, index=[0])
        # print(list)
        # df2 = pd.DataFrame(list, columns=['tauxDeVariation'])
        # print(df2)
        # df3 = df2
        # print(df3)
    # print('-----------------------------------Le resultats renvoyées-------------------------------')
    dfx = pd.DataFrame(data_)
    dfy = dfx.to_dict(orient='records')
    # print(dfy)
    return dfy


# Fonction permettant d'obtenir les metriques d'une ligne entre 2 dates
def metric_date_between():
    dateDebut = request.args.get('dateDebut')
    dateFin = request.args.get('dateFin')

    numero = request.args.get('numero')

    if dateDebut is not None and dateFin is not None and numero is not None:
        data = select_query_date_between(''' SELECT DISTINCT inv.service_id, inv.ip_olt, inv.slot, inv.pon , inv.vendeur, inv.nom_olt, inv.debitup, inv.debitdown,
                                                     mt.oltrxpwr, mt.ontrxpwr, inv.created_at::date 
                                                    FROM inventaireglobal_network_bis inv, metric_seytu_network mt
                                                    WHERE inv.service_id = mt.numero
                                                    AND inv.ip_olt = mt.olt_ip
                                                    AND inv.created_at::date BETWEEN '{}' AND '{}'
                                                    AND inv.service_id = '{}'
                                                    ORDER BY inv.created_at::date DESC ;  ''', dateDebut, dateFin,
                                         numero)
        return data

    else:
        return "Veuillez saisir les dates"


# Fonction permettant d'afficher le resultats du diagnostic
def resultat_diagnostic():
    numero = request.args.get('numero')
    if numero is not None:
        # recuperer les données
        data = select_query_argument(''' SELECT * FROM real_time_diagnostic WHERE numero = '{}' ORDER BY DATE DESC ''', numero)
        return data
    else:
        return "Vous devez saisir un numero"


# Fonction permettant de faire de la recherche élargie
def recherche_elargie():
    con = None
    #text = request.args.get('text')
    #[text for text in request.args.keys()]
    #numero = request.args.get('numero')
    #ip = request.args.get('ip')
    #vendeur = request.args.get('vendeur')
    text = request.args.get('recherche')
    #text_int = request.args.get('textint')

    try:
        con = connect()
        df = pd.read_sql(''' Select Distinct mtp.numero, mtp.ip, mtp.vendeur, mtp.nom_olt, msn.oltrxpwr, msn.ontrxpwr,
                                             ign.slot, ign.pon, ign.debitup, ign.debitdown, mtp.anomalie, mtp.created_at
                                    FROM maintenance_predictive_ftth mtp
                                    INNER JOIN metric_seytu_network msn ON (mtp.numero = msn.numero  and mtp.ip = msn.olt_ip )
                                    INNER JOIN inventaireglobal_network_bis ign ON (msn.numero = ign.service_id and msn.olt_ip = ign.ip_olt)
                                    AND ((ign.ip_olt='{}') OR (ign.vendeur='{}') OR (mtp.numero='{}') OR (ign.nom_olt='{}') OR (ign.slot::varchar(255)='{}') OR (ign.pon::varchar(255)='{}') )
                                    ORDER BY mtp.created_at DESC  ;'''.format(text, text, text, text, text, text), con)
        data = df.to_dict(orient='records')
        con.commit()
    except(Exception, psycopg2.DataError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return data
    #else:
        #return {'message': "Vous devez saisir un text"}

    #try:



# fonction creation de la table parc_constitution_ftth
def create_table():
    con = connect()
    cursor = con.cursor()
    try:
        create_table_query = ''' CREATE TABLE IF NOT EXISTS real_time_diagnostic
                        (
                           id serial PRIMARY KEY,
                           numero int,
                           vendeur varchar(100),
                           debit_up numeric,
                           debit_down numeric,
                           statut varchar(100),
                           date timestamp
                            
                        ); '''
        cursor.execute(create_table_query)
        con.commit()
        print(" Table créée successfully ...  ")
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if con:
            cursor.close()
            con.close()


# La fonction permettant de stocker sur la table real_time_diagnostic
def to_real_time_diagnostic(numero):
    vendeur = get_vendeur(numero)
    # Pour les Clients dont le vendeur est Nokia
    if vendeur == 'Nokia':
        getProvisioning(numero)
    # Pour les Clients dont le vendeur est Huawei
    if vendeur == 'Huawei':
        configurationClientsHuawei(numero)

# Chargement de la table parc_constitution_ftth
# if __name__ == '__main__':


# fonction derniere heure de coupure
# def get_derniere_heure_coupure():
