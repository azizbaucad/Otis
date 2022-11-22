from pysnmp.hlapi import *
import pandas as pd
from script.function import data_inventaire, data_invent
import datetime


def fiberCut(serviceId):
    """
    fonction permettant de diagnostiquer s'il y a coupure
    de fibre.
    Arguments:
         - serviceId: numéro de téléphone du client

    """

    df = data_inventaire(serviceId)

    # print(str(df[df['serviceId'] == serviceId]['ont_index'].values[0]))

    try:
        index, ip, _ont_, vendeur, pon = str(df[df['serviceId'] == serviceId]['ont_index'].values[0]), \
                                         str(df[df['serviceId'] == serviceId]['ip_olt'].values[0]), \
                                         str(df[df['serviceId'] == serviceId]['ont_id'].values[0]), \
                                         str(df[df['serviceId'] == serviceId]['vendeur'].values[0]), \
                                         str(df[df['serviceId'] == serviceId]['pon'].values[0])

        ### Diagnostic en fonction de l'équipement ###

        # Pour Nokia
        if vendeur == "Nokia":

            # Extract current ONT alarms

            oid_ont = "1.3.6.1.4.1.637.61.1.35.10.4.1.2" + "." + index  # oid de Current OLT alarms   : 1.3.6.1.4.1.637.61.1.35.10.4.1.2
            currentAlarmList = []

            for (errorIndication,
                 errorStatus,
                 errorIndex,
                 varBinds) in getCmd(SnmpEngine(),
                                     CommunityData('t1HAI2nai'),
                                     UdpTransportTarget(transportAddr=(ip, 161)),
                                     ContextData(),
                                     ObjectType(ObjectIdentity(oid_ont)),
                                     lexicographicMode=False,
                                     lookupMib=False, timeout=2.0, retries=20):

                if errorIndication:
                    raise Exception('SNMP getCmd error {0}'.format(errorIndication))
                else:
                    for varBind in varBinds:
                        temp_ = bin(int(varBind[1].prettyPrint()))[::-1][:-2]
                        for i in range(len(temp_)):
                            if temp_[i] == "1":
                                currentAlarmList.append(str(i + 1))

            # Check if the alarm matches with Loss of signal(1),Inactive(15),Loss of Frame(16) and Signal fail(17)

            for i in currentAlarmList:
                if i in ["1", "15", "16", "17"]:
                    checkFiberCut = "OK"
                else:
                    checkFiberCut = "KO"

            # Customer Rx optical power

            oid_ont1 = "1.3.6.1.4.1.637.61.1.35.10.14.1.2" + "." + index  # oid de ontRxpower Nokia: 1.3.6.1.4.1.637.61.1.35.10.14.1.2

            for (errorIndication,
                 errorStatus,
                 errorIndex,
                 varBinds) in getCmd(SnmpEngine(),
                                     CommunityData('t1HAI2nai'),
                                     UdpTransportTarget(transportAddr=(ip, 161)),
                                     ContextData(),
                                     ObjectType(ObjectIdentity(oid_ont1)),
                                     lexicographicMode=False,
                                     lookupMib=False, timeout=2.0, retries=20):

                if errorIndication:
                    raise Exception('SNMP getCmd error {0}'.format(errorIndication))
                else:
                    for varBind in varBinds:
                        ontpower = varBind[1].prettyPrint()

            # voir si ontpower=="2147483647" correspond à rx optical power non disponible pour Nokia

            if (
                    ontpower == "32768" and checkFiberCut == "OK"):  # la valeur 32768 signifie que ont rx optical power est indisponible
                return {
                    'status': 'ko',
                    "anomalie": "Coupure fibre",
                    "etat": "Critique",
                    "description": "Coupure de fibre optique",
                    "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
                                       "Faire une mesure de réflectometrie pour localisation du point de coupure."]
                }
            else:
                return {'status': 'ok', 'description': 'coupure fibre Non'}

        # Pour Huawei

        elif vendeur == "Huawei":

            # Current ONT alarms for customer: OntLastDownCause
            oid_ont = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24" + "." + index + "." + _ont_

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

            if result in ["1", "2", "3", "4"]:
                checkFiberCut = "OK"
            else:
                checkFiberCut = "KO"

            # Customer Rx optical power

            oid_ont1 = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4" + "." + index + "." + _ont_  # oid de ontRxpower: 1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4

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
                        ontpower = varBind[1].prettyPrint()

            if (ontpower == "2147483647" and checkFiberCut == "OK"):
                return {
                    'status': 'ko',
                    "anomalie": "Coupure fibre",
                    "etat": "Critique",
                    "description": "Coupure de fibre optique",
                    "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
                                       "Faire une mesure de réflectometrie pour localisation du point de coupure."]
                }
            else:
                return {'status': 'ok', 'description': 'coupure fibre Non'}

    except:
        pass


def scriptMaintenanceFiberCut(taille, pas):
    df = data_invent()
    df = df[taille:(taille + pas)]
    size = len(df.index)
    listNumero = []
    listPon = []
    listIpOlt = []
    listEtat = []
    listAnomalie = []
    listVendeur = []
    listOlt = []
    listSlot = []
    listSlot = []
    listDate = []
    start_time = datetime.now()
    for i in range(size):
        # if i == 100:
        #     break
        try:
            serviceId = df['serviceId'].values[i]
            pon = df['pon'].values[i]
            ip_olt = df['ip_olt'].values[i]
            vendeur = df['vendeur'].values[i]
            slot = df['slot'].values[i]
            nomOlt = df['nomOlt'].values[i]
            print(i)
            data = fiberCut(serviceId)
            statut = data['status']
            etat = data['etat']
            if statut == 'ko' and etat != 'Moyen':
                anomalie = data['anomalie']
                listNumero.append(serviceId)
                listPon.append(pon)
                listIpOlt.append(ip_olt)
                listVendeur.append(vendeur)
                listSlot.append(slot)
                listOlt.append(nomOlt)
                listEtat.append(etat)
                listAnomalie.append(anomalie)
                listDate.append(datetime.today().strftime('%Y-%m-%d'))
        except:
            pass
    df = pd.DataFrame(
        zip(listNumero, listOlt, listPon, listSlot, listIpOlt, listVendeur, listAnomalie, listEtat, listDate),
        columns=['numero', 'nom_olt', 'pon', 'slot', 'ip', 'vendeur', 'anomalie', 'criticite', 'date'])

    # filename = pathMaintenance() + "fiberCut_ftth_" + str(numFile) + ".csv"
    # df.to_csv(filename, sep=";", index=False)
    # create_table_maintenance()

    #TODO : Chargement de la Table maintenance_predictive_ftth à revoir
    #maintenance_to_database(df)

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
