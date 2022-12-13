from pysnmp.hlapi import *
from script.function import data_inventaire, data_infos_huawei_conf
from script.conf import connect
#from app import date_start
import datetime
from datetime import datetime as dt
import warnings
from script.getSignalOptical import getOpticalSignal

warnings.filterwarnings("ignore")

def configurationClientsHuawei(serviceId):
    """ fonction permettant d'avoir la configuration des clients au niveu des
        équiepemnts
        Arguments:
        serviceId: le numéro du client
        """
    date_start = datetime.datetime.now()
    df = data_inventaire(serviceId)
    _index_, ip, _ont_, pon, slot, vendeur = str(df[df['serviceId'] == serviceId]['ont_index'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['ip_olt'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['ont_id'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['pon'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['slot'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['vendeur'].values[0])
    #print('----------------infos--------------')
    #print(_index_, ip, _ont_, pon, slot, vendeur)
    #print('---------------------resultats renvoyes-----------------')
    #print(df)
    df_final = data_infos_huawei_conf(ip, pon, slot)
    #print('------------------------resultats final----------------')
    #print(df_final)
    # print(df_final)
    # index = df_final[(df_final["ip"] == ip) & (df_final["onuId"] == int(_ont_)) & (df_final["pon"] == int(pon)) & (
    #         df_final["slot"] == int(slot))]["index"].values[0]
    # print(ip)
    # print(pon)
    # print(slot)
    # print(_ont_)
    down_str = df_final[(df_final["ip"] == ip) & (df_final["onuId"] == int(_ont_)) & (df_final["pon"] == int(pon)) & (df_final["slot"] == int(slot))]["nomTrafDown"].values[0]
    up_str = df_final[(df_final["ip"] == ip) & (df_final["onuId"] == int(_ont_)) & (df_final["pon"] == int(pon)) & (df_final["slot"] == int(slot))]["nomTrafUp"].values[0]

    oid_index = "1.3.6.1.4.1.2011.5.14.3.8.1.2"
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('OLT@osn_read'),
                              UdpTransportTarget(transportAddr=(ip, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid_index)),
                              lexicographicMode=False,
                              lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            #print('--------------------------Les donnes du reseua----------------------')
            #print(errorIndication, errorStatus, errorIndex, varBinds)
            for varBind in varBinds:
                if varBind[1].prettyPrint() == down_str:
                    id_dwstr = varBind[0].prettyPrint().split(".")[-1]
                elif varBind[1].prettyPrint() == up_str:
                    id_upstr = varBind[0].prettyPrint().split(".")[-1]

    oid_debit_up = "1.3.6.1.4.1.2011.5.14.3.8.1.5" + "." + id_dwstr

    oid_debit_down = "1.3.6.1.4.1.2011.5.14.3.8.1.5" + "." + id_upstr

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_debit_up)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                debit_up = int(varBind[1].prettyPrint()) / 1000

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_debit_down)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                debit_down = int(varBind[1].prettyPrint()) / 1000
                if debit_down <= 39:
                    offre = "FIBRE BI"
                    # 20 down
                    break
                elif debit_down > 39 and debit_down <= 59:
                    offre = "FIBRE MAX"
                    # 40 down
                    break
                elif debit_down > 59 and debit_down <= 99:
                    offre = "FIRBE MEGA"
                    # 60 down
                    break
                else:
                    offre = "FIRBE MEGA PLUS"
                    # 100 down
                    break
    # oid rx power ont
    oid_rxPower = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4" + "." + str(_index_) + "." + _ont_

    # oid operstatus
    oid_operstatus = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15." + str(_index_) + "." + str(
        _ont_)  # Up(1),Down(2),Unknown(-1)

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_operstatus)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                #print('-----------------------Les donnes du reseau pour statut-------------------------')
                #print(varBind)
                operstatus = varBind[1].prettyPrint()
                #print('----------------------------------Operstattus----------------------------')
                #print(varBind[1])
                if operstatus == "1":
                    # TODO: les débits doivent etre intégres ici
                    statut = "Actif"
                else:
                    statut = "Inactif"

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_rxPower)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                rxPower = int(varBind[1].prettyPrint()) / 100
                if int(varBind[1].prettyPrint()) == 2147483647:
                    qualitySignal = "Signal indisponible"
                elif rxPower <= -30:
                    qualitySignal = "Tres degrade"
                elif ((rxPower > -30 and rxPower <= -27) or rxPower > 10):
                    qualitySignal = "Degrade"
                else:
                    qualitySignal = "Normal"
    #print(debit_up, debit_down, statut, qualitySignal)

    #print('-------------------recuperation des données-------------')

    #Intégration de la fonction fiberCut pour obtenir les données sur les anomalies

    # Current ONT alarms for customer: OntLastDownCause
    oid_ont = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24" + "." + _index_ + "." + _ont_

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_ont)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=20):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                result = varBind[1].prettyPrint()
    # Check if the alarm matches with Loss of signal(1),Loss of signal for ONUi or Loss of burst for ONUi(2),Loss of frame of ONUi(3),Signal fail of ONUi(4)

    #print(f'Verifier ce resultat: {result}')
    if result in ["1", "2", "3", "4"]:
        checkFiberCut = "OK"
    else:
        checkFiberCut = "KO"

    # Customer Rx optical power

    oid_ont1 = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4" + "." + _index_ + "." + _ont_  # oid de ontRxpower: 1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4
    #anomalie = None
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_ont1)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=20):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                #print('---------------Les donnees du reseau dans FiberCut---------------------')
                #print(varBind)
                ontpower = varBind[1].prettyPrint()

    if (ontpower == "2147483647" and checkFiberCut == "OK"):
        if getOpticalSignal(serviceId) == 0:
            debit_up = 0
            debit_down = 0
        anomalie = "Coupure fibre"
        #debit_up = 0
        #debit_down = 0
        #print(anomalie, debit_up, debit_down)
        # return {
        #     'status': 'ko',
        #     "anomalie": anomalie,
        #     "etat": "Critique",
        #     "description": "Coupure de fibre optique",
        #     "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
        #                        "Faire une mesure de réflectometrie pour localisation du point de coupure."]
        # }
    else:
        anomalie = "Pas de coupure de fibre"
        #print(anomalie, debit_up, debit_down)
        #return {'status': 'ok', 'description': 'coupure fibre Non', 'anomalie': anomalie, 'Numero': serviceId}

    #Fin de l'intégration fiberCut

    # Inserer les données dans la table real_time_dignostic
    # A optimiser
    #print(f'Numero: {serviceId}, Vendeur: {vendeur}, Debit_up: {debit_up}, Debit_down: {debit_down}, Statut: {statut}, Anomalie: {anomalie}')
    con = connect()
    cursor = con.cursor()
    #cursor.execute(''' TRUNCATE TABLE real_time_diagnostic ''')
    cursor.execute(''' INSERT INTO real_time_diagnostic (numero, vendeur, anomalie, debit_up, debit_down, statut, signal)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s) ''',
                   (serviceId, vendeur, anomalie, debit_up, debit_down, statut, qualitySignal), )
    con.commit()
    #print()

    #return 0
    #print(f'Numero: {serviceId}, Vendeur: {vendeur}, Debit_up: {debit_up}, Debit_down: {debit_down}, Statut: {statut}')
    # list_ = {
    #         "numero": serviceId,
    #         "vendeur": vendeur,
    #         "anomalie": anomalie,
    #         "max_up": debit_up,
    #         "max_down": debit_down,
    #         "statut": statut,
    #         "quality_signal": qualitySignal}
    #
    # print(type(list_))
    # return list_
    return "Diagnostic en cours..."

# print(configurationClientsHuawei('338276153'))
if __name__ == '__main__':
    list_num = ['338224541', '338650432', '338650115', '338670493']
    for num in list_num:

        print(configurationClientsHuawei(num))

