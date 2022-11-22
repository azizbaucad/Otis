from pysnmp.hlapi import *
from script.function import data_inventaire, data_infos_huawei_conf
from script.conf import connect
#from app import date_start
import datetime
from datetime import datetime as dt

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
            print('--------------------------Les donnes du reseua----------------------')
            print(errorIndication, errorStatus, errorIndex, varBinds)
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
                operstatus = varBind[1].prettyPrint()
                if operstatus == "1":
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
                    qualitySignal = "Très dégradé"
                elif ((rxPower > -30 and rxPower <= -27) or rxPower > 10):
                    qualitySignal = "Dégradé"
                else:
                    qualitySignal = "Normal"
    #print(debit_up, debit_down, statut, qualitySignal)
    # Inserer les données dans la table real_time_dignostic
    con = connect()
    cursor = con.cursor()
    cursor.execute(''' INSERT INTO real_time_diagnostic (numero, vendeur, debit_up, debit_down, statut, date) 
                                    VALUES (%s, %s, %s, %s, %s, %s) ''',
                   (serviceId, vendeur, debit_up, debit_down, statut, dt.now()), )
    con.commit()
    print("Insertion is running....")
    #print('-------------------recuperation des données-------------')
    print(f'Numero: {serviceId}, Vendeur: {vendeur}, Debit_up: {debit_up}, Debit_down: {debit_down}, Statut: {statut}')
    return {"offre": offre,
            "MaxUp": debit_up,
            "MaxDown": debit_down,
            "statutModem": statut,
            "qualitySignal": qualitySignal}

# print(configurationClientsHuawei('338276153'))