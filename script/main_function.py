import psycopg2
from script.conf import *
import pandas as pd
from datetime import datetime


def simple_inventaire():
    data = select_query(''' SElect * from historique_diagnostic limit 10 ''')
    return data


# fonction doublon
def get_doublon():
    numero = request.args.get('numero')
    if numero is None or numero == "":
        data = select_query('''Select db.service_id, db.nom_olt, db.ip_olt, db.vendeur, db.created_at::date , mt.oltrxpwr, mt.ontrxpwr
                                   From doublons_ftth as db, metric_seytu_network as mt
                                   where db.service_id = mt.numero
                                   and db.ip_olt = mt.olt_ip order by db.created_at::date desc''')
        return data
    else:
        data = select_query_argument('''Select db.service_id, db.created_at::date, db.nom_olt, db.ip_olt, db.vendeur, mt.oltrxpwr, mt.ontrxpwr
                                           From doublons_ftth as db, metric_seytu_network as mt
                                           where db.service_id = mt.numero 
                                           and db.ip_olt = mt.olt_ip
                                           and db.service_id = '{}'  order by db.created_at::date desc''', numero)
        return data


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
            '''Select numero, ip, anomalie, nom_olt,  count(numero) as Dureee FROM maintenance_predictive_ftth WHERE date BETWEEN '{}'  AND  '{}' GROUP BY numero, ip, anomalie, nom_olt HAVING COUNT(numero) = {} ''',
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
        dict = {'debitSouscrit': debitSouscrit, 'Taux': taux, 'offre': row.offre, 'debitdown': row.debitdown, 'debitup': row.debitup, 'ip_olt': row.ip_olt, 'nom_olt': row.nom_olt, 'pon': row.pon, 'service_id': row.service_id, 'slot': row.slot}
        data_.append(dict)
        df2 = pd.DataFrame(data=dict, index=[0])
        # print(list)
        # df2 = pd.DataFrame(list, columns=['tauxDeVariation'])
        # print(df2)
        # df3 = df2
        # print(df3)
    #print('-----------------------------------Le resultats renvoyées-------------------------------')
    dfx = pd.DataFrame(data_)
    dfy = dfx.to_dict(orient='records')
    #print(dfy)
    return dfy
# fonction derniere heure de coupure
# def get_derniere_heure_coupure():
