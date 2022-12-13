import csv , json
from dateutil import parser
import psycopg2
from psycopg2 import Error
from script.conf import connect, select_query_two_arg, truncate_query, select_query, select_query_date_between, select_query_argument
import pandas as pd
from datetime import datetime, date, time
#from datetime import date
from script.function import get_vendeur
import datetime as dt
import time
from flask import request
from script.confClientsNokia import getProvisioning
from script.confClientsHuawei import configurationClientsHuawei


# from datetime

# fonction doublon
def get_doublon():
    numero = request.args.get('numero')
    if numero is None:
        return "Veuillez Saisir un numéro"
    else:
        data_ = select_query_argument('''
                                          SELECT db.service_id, db.ip_olt, db.slot, db.pon, db.vendeur, db.nom_olt, mt.oltrxpwr, mt.ontrxpwr, TO_CHAR(db.created_at::date, 'dd-mm-yyyy') date
                                                 FROM doublons_ftth db, metric_seytu_network mt 
                                                 WHERE  db.service_id like '%{}' 
                                                 AND db.service_id = mt.numero
                                                 AND db.ip_olt = mt.olt_ip
                                                 ORDER BY db.created_at::date desc ''', numero)
        print('-------Data renvoyé---------')
        print(data_)
        return data_



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
        data = select_query_argument('''SELECT DISTINCT service_id, offre,vendeur, debitup, debitdown, ip_olt,nom_olt,slot,pon,  to_char(created_at::date, 'dd-mm-yyyy')
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


# Historique coupure entre deux dates
def get_historique_coupure_date_between():
    numero = request.args.get('numero')
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    #date_debut = datetime.strptime(date_debut, '%Y-%m-%d')
    #date_fin = datetime.strptime(date_fin, '%Y-%m-%d')
    if numero is not None and date_debut is None or date_fin is None:
        data = get_historique_coupure_six_mois()


        return data

    elif numero is None and date_debut is not None and date_fin is not None:
        data = select_query_two_arg('''
                                        SELECT numero, pon, slot, ip, nom_olt, vendeur, anomalie, TO_CHAR(date, 'dd-mm-yyyy') date
                                            FROM maintenance_predictive_ftth
                                            WHERE date BETWEEN '{}' AND '{}'
                                            ORDER BY date  DESC
                                     ''',
                                     date_debut, date_fin)


        return data


    elif numero is not None and date_debut is not None and date_fin is not None:
        data = select_query_date_between(
            ''' SELECT numero, pon, slot, ip, nom_olt, vendeur, anomalie, TO_CHAR(date, 'dd-mm-yyyy') date
                FROM maintenance_predictive_ftth
                WHERE date BETWEEN '{}' AND '{}'
                AND numero like '%{}' order by date DESC
            ''', date_debut, date_fin, numero
        )



        return data
    # else:
    #     return "Veuillez entrer les dates"
    else:
        return "Veuillez donner un numero"


# Hisorique coupure de plus de 6 mois
def get_historique_coupure_six_mois():
    numero = request.args.get('numero')
    if numero is not None:

        data = select_query_argument(
            '''
                 SELECT numero, pon, slot, ip, nom_olt, vendeur, anomalie, TO_CHAR(date, 'dd-mm-yyyy') date
                  FROM maintenance_predictive_ftth
                  WHERE date BETWEEN now()::date - interval '6' MONTH AND now()::date
                  AND numero like '%{}' ORDER BY DATE DESC
            ''',
            numero
        )


        return data
    else:
        return 'Veuillez saisir un numero'


# la fonction taux d'utilisation avec débit
def taux_utilisation_debit_old():
    data_ = []
    numero = request.args.get('numero')
    data = select_query_argument(''' SELECT DISTINCT service_id, offre, debitup, debitdown, ip_olt,nom_olt, slot, pon, created_at
                                        FROM inventaireglobal_network_bis
                                        WHERE  service_id like '%{}' ''', numero)









    

    #df = pd.DataFrame(data)
    print('----------------Les données renvoyé est-----------------------')
    print(data, type(data))
    #print('------------Les données renvoyés en json-------------')
    data_json = json.loads(data)
    #print(data_json, type(data_json))
    #print('----------------Data Transformateted in a dataFrame--------')
    df = pd.DataFrame(data_json)
    #print(df, type(df))
    #for row in
    #df = pd.DataFrame(data)
    #print('---------------Le DataFrame renvoyé est ------------------------')
    #print(df)
    i = 0

    print('-------------------------------Data Retourne----------------------')
    #print(df)
    #for row in df.itertuples():
    #    print(f'Date : {row.created_at}')
    return  data
    #
    #
    #     #date_str = dt.datetime.strptime(str(row.created_at), '%Y-%m-%d').strftime('%d-%m-%Y')
    #
    #
    #
    #     if row.offre == "FIBRE BI":
    #         debitSouscrit = 20
    #     elif row.offre == "FIBRE MAX":
    #         debitSouscrit = 40
    #     elif row.offre == "FIBRE MEGA":
    #         debitSouscrit = 60
    #     else:
    #         debitSouscrit = 100
    #     debitdown = row.debitdown
    #     taux = (debitdown / debitSouscrit) * 100
    #
    #     dict = {'debitSouscrit': debitSouscrit, 'Taux': taux, 'offre': row.offre, 'debitdown': row.debitdown,
    #             'debitup': row.debitup, 'ip_olt': row.ip_olt, 'nom_olt': row.nom_olt, 'pon': row.pon,
    #             'service_id': row.service_id, 'slot': row.slot, 'date': row.created_at}
    #     data_.append(dict)
    #     #df2 = pd.DataFrame(data=dict)
    # dfx = pd.DataFrame(data_)
    # dfy = dfx.to_json(orient='records')
    # print('-----------------------------Les données finales renvoyées corresponds à -----------------')
    # print(dfy, type(dfy))
    #
    # return dfy


# Fonction permettant d'obtenir les metriques d'une ligne entre 2 dates
def metric_date_between():
    dateDebut = request.args.get('dateDebut')
    dateFin = request.args.get('dateFin')
    #dateDebut = datetime.strptime(dateDebut, '%y-%d-%m %H:%M')
    #dateDebut = datetime.strptime(dateFin, '%y-%d-%m %H:%M')
    #print(f" Date Format Debut: {dateDebut}")
    #print(f" Date Format Debut: {dateFin}")
    #print(f'Date Format Fin: {datetime.strptime(dateFin, "%d-%m-%y %H:%M"}')
    print(f'Date Debut is :  {dateDebut, type(dateDebut)} and Date Fin is : {dateFin, type(dateFin)}')
    #dateparser.parse(dateDebut, date_formats=[''])

    numero = request.args.get('numero')

    if dateDebut is not None and dateFin is not None and numero is not None:
        data = select_query_date_between(''' SELECT DISTINCT inv.service_id, inv.ip_olt, inv.slot, inv.pon , inv.vendeur, inv.nom_olt, inv.debitup, inv.debitdown,
                                                     mt.oltrxpwr, mt.ontrxpwr, to_char(inv.created_at::date, 'dd-mm-yyyy') as date 
                                                    FROM inventaireglobal_network_bis inv, metric_seytu_network mt
                                                    WHERE inv.service_id = mt.numero
                                                    AND inv.ip_olt = mt.olt_ip
                                                    AND to_char(inv.created_at::date, 'dd-mm-yyyy') BETWEEN '{}' AND '{}'
                                                    AND inv.service_id = '{}'
                                                    ORDER BY to_char(inv.created_at::date, 'dd-mm-yyyy') DESC ;  ''', dateDebut, dateFin,
                                         numero)
        return data

    else:
        return "Veuillez saisir les dates"


# Fonction permettant de faire le diagnostic à temps réesl
def monitoring():
    numero = request.args.get('numero')

    date_start = request.args.get('dateDebut')
    #date_start = datetime.date.fromisoformat(date_start)
    #date_start = date_start.isoformat()
    print(f'Date Start is : {date_start, type(date_start)}')
    # picasoBirthDate = datetime.date.fromisoformat(birthday_Picaso);
    # date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
    date_start = dt.datetime.strptime(date_start, '%d-%m-%Y %H:%M:%S')
    print(f'Date Start : {date_start, type(date_start)}')

    interval_to_sleep_int = int(request.args.get('interval'))
    # interval_to_sleep_int = interval_to_sleep_int * 60
    interval_to_sleep = dt.timedelta(minutes=interval_to_sleep_int)

    date_end = request.args.get('dateFin')
    #date_end = dt.datetime.fromisoformat(date_end)
    date_end = dt.datetime.strptime(date_end, '%d-%m-%Y %H:%M:%S')
    print(f'Date End : {date_end, type(date_end)}')

    date_start_iso = date_start.isoformat(' ', 'seconds')
    date_end_iso = date_end.isoformat(' ', 'seconds')

    if numero is not None:
        # truncate_query(''' TRUNCATE TABLE real_time_diagnostic''')

        while dt.datetime.now().isoformat(' ', 'seconds'):
            # time.sleep(1)
            # print('Be Patient Otis...')
            if dt.datetime.now().isoformat(' ', 'seconds') == date_start_iso:
                print('Otis is now start...')
                while dt.datetime.now().isoformat(' ', 'seconds'):

                    to_real_time_diagnostic(numero)
                    time.sleep(interval_to_sleep_int * 60)
                    date_start = date_start + interval_to_sleep

                    # print(f'Date start now: {date_start}')

                    if date_start > date_end or date_start == date_end:
                        # to_real_time_diagnostic(numero)
                        # print('Otis is Dead first one...')
                        # print(f'Date end iso : {date_end_iso}')
                        break
            # if 10000 <= number <= 30000:
            if dt.datetime.now().isoformat(' ', 'seconds') == date_end_iso or dt.datetime.now().isoformat(
                    ' ', 'seconds') > date_end_iso:
                # print('Otis is now Dead...')
                break

        # recuperer les données
        # data = select_query_argument(''' SELECT * FROM real_time_diagnostic ORDER BY DATE ASC ''', numero)
        return "Fin du diagnostic"

    else:
        return "Vous devez saisir un numéro"


# Fonction permettant d'afficher le resultats du diagnostic
def resultat_diagnostic():
    numero = request.args.get('numero')
    if numero is not None:
        # recuperer les données
        data = select_query_argument(''' SELECT numero, vendeur, anomalie, debit_up, debit_down, statut, signal, TO_CHAR(created_at, 'dd-mm-yyyy HH:MI:SS') date
                                                FROM real_time_diagnostic WHERE numero = '{}' ORDER BY created_at DESC ''',
                                     numero)
        return data
    else:
        return "Vous devez saisir un numero"


# Fonction permettant de faire de la recherche élargie
def recherche_elargie():
    con = None
    text = request.args.get('recherche')

    try:
        con = connect()
        df = pd.read_sql(''' Select Distinct mtp.numero, mtp.ip, mtp.vendeur, mtp.nom_olt, msn.oltrxpwr, msn.ontrxpwr,
                                             ign.slot, ign.pon, ign.debitup, ign.debitdown, mtp.anomalie, mtp.created_at
                                    FROM maintenance_predictive_ftth mtp
                                    INNER JOIN metric_seytu_network msn ON (mtp.numero = msn.numero  and mtp.ip = msn.olt_ip )
                                    INNER JOIN inventaireglobal_network_bis ign ON (msn.numero = ign.service_id and msn.olt_ip = ign.ip_olt)
                                    AND ((ign.ip_olt='{}') OR (ign.vendeur='{}') OR (mtp.numero='{}') OR (ign.nom_olt='{}') OR (ign.slot::varchar(255)='{}') OR (ign.pon::varchar(255)='{}') )
                                    ORDER BY mtp.created_at DESC  ;'''.format(text, text, text, text, text, text), con)

        data = df.to_json(orient='records')
        con.commit()

        #df = pd.DataFrame(data)
        #print('-----------------------------Le DataFrame------------------')
        #print(df)
        #i = 0
        #for row in df.itertuples():
            #print(f'Data: {row.numero, row.ip, row.vendeur, row.created_at, type(row.created_at)}')
            #date_str = dt.datetime.strptime(str(row.created_at), '%Y-%m-%d').strftime('%d-%m-%Y')
            #print('---------------------')

    except(Exception, psycopg2.DataError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return data


# Fonction permettant d'obtenir la derniere heure de coupure
def derniere_heure_coupure():
    numero = request.args.get('numero')
    if numero is not None:
        data = select_query_argument('''SELECT numero, pon, slot, nom_olt, ip, vendeur, anomalie, criticite, to_char(created_at::date, 'dd-mm-yyyy') date
                                               FROM maintenance_predictive_ftth
                                               WHERE numero = '{}' 
                                               ORDER BY created_at::date DESC limit 1''', numero)
        return data
    else:
        return "Vous devez saisir un numéro"


# fonction creation de la table parc_constitution_ftth
def create_table():
    con = connect()
    cursor = con.cursor()
    cursor.execute('''DROP TABLE real_time_diagnostic''')
    try:
        create_table_query = ''' CREATE TABLE IF NOT EXISTS real_time_diagnostic
                        (
                           id SERIAL PRIMARY KEY,
                           numero varchar,
                           vendeur varchar,
                           anomalie varchar,
                           debit_up numeric,
                           debit_down numeric,
                           statut varchar,
                           signal varchar,
                           created_at TIMESTAMP DEFAULT Now() 
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


# Ingestion du fichier parc dans PostgreSQL
# Fonction de transformation du fichier
def transform_file():
    try:
        lecture = csv.reader(open("constitution.csv", "rU", newline=None), delimiter=';')
        if lecture != "":
            print("-----------Lecture en cours.........................")
        ecriture = csv.writer(open("constitution_output.csv", 'w'), delimiter=',')
        if ecriture != "":
            print("-----------------------Ecriture en cours---------------------")
        print("------------Transformation en cours---------------------")
        ecriture.writerows(lecture)
        print("Ecriture resussi...............")
        if ecriture.writerows(lecture) != "":
            print("Ecriture.................................")

    except:
        print("---------------Tranformation impossible-----------------------------------------")


# Fonction insert_constitution pour l'ingestion des données
def insert_constitution():
    con = connect()
    cursor = con.cursor()
    df = pd.read_csv("constitution_output.csv", sep=",", on_bad_lines='skip', encoding_errors='ignore',
                     engine='python')
    df = df.where(pd.notnull(df), None)
    for index, row in df.iterrows():
        cursor.execute(
            ''' 
                INSERT INTO parc_constitution_ftth (ncli, nd, nom, prenom, etat_client, contact_mobile_client, acces_reseau, zone_rs, fo_type_eqpt_am, fo_nom_eqpt_am, fo_type_eqpt_av, fo_nom_eqpt_av, libelle_rsp_fo )
                                                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  ''',
            (row.NCLI, row.ND, row.NOM, row.PRENOM1, row.ETAT_DU_CLIENT, row.CONTACT_MOBILE_CLIENT, row.ACCES_RESEAU,
             row.ZONE_RS, row.FO_TYPE_EQPT_1_AM, row.FO_NOM_EQPT_1_AM, row.FO_TYPE_EQPT_1_AV, row.FO_NOM_EQPT_1_AV,
             row.LIBELLE_RSP_FO),
        )
        con.commit()
        print(
            '...Insertion en cours............................................................................................................')
    con.commit()
    cursor.close()

def test_sql():
    con = connect()
    df = pd.read_sql('''Select * from doublons_ftth limit 2''', con)
    #data = df.to_dict(orient='records')
    data = df.to_json(orient='records', lines=True)
    print(data, type(data))
    con.commit()
    con.close()




def taux_utilisation_debit():
    data_ = []
    numero = request.args.get('numero')
    if numero is not None :

        data = select_query_argument('''SELECT DISTINCT service_id, offre,vendeur, debitup, debitdown, ip_olt,nom_olt,slot,pon,  to_char(created_at::date, 'dd-mm-yyyy') date 
                    FROM inventaireglobal_network_bis WHERE service_id like '%{}' ''', numero)

    data_json = json.loads(data)
    #print(data, type(data))
    #print('---------------------------------- JSON ------------------')
    #print(data_json, type(data_json))
    df = pd.DataFrame(data_json)
    #print('---------------------------------- DataFrame -------------')
    #print(df, type(df))
    list_ = []
    i = 0
    for row in df.itertuples():

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

        list1 = {'debitSouscrit':debitSouscrit, 'taux': taux, 'offre': row.offre, 'debitdown': row.debitdown, 'debitup': row.debitup, 'ip_olt': row.ip_olt, 'nom_olt': row.nom_olt, 'pon': row.pon, 'date': row.date}
        #print(list, type(list))
        list_.append(list1)
        #print('------------------------List-----------------')
        #print(list_, type(list_))

    #print('-------------------List renvoie OK----------------------')
    #print(list_, type(list_))
    json_data = json.dumps(list_)
    print('------------------JSON DUMPS----------------')
    print(json_data, type(json_data))

    return json_data

        #list_.append(d)
        #data_df = data_.append(dict)
        #print(data_df)
        #dta = l.append(dict)
        #list_.append(dict)
        #print(list_.append(dict))
    #print(dta)
        
