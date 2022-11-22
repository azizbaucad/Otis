# Pour Nokia
import re
from script.confClientsHuawei import *
from script.fiberCut import fiberCut
from script.getSignalOptical import getOpticalSignal
from script.oltPowerUnderLimit import oltPowerUnderLimit
from script.ontUnderLimit import ontPowerUnderLimit
from script.powerSupplydown import powerSupplyDown
from datetime import datetime as dt

def getMaxDebit(ip, idService, direction="up"):
    """
    Fonction permettant de calculer le débit up maxi du client
    provisionné:
    Arguments:
    ip:@IP de l'OLT
    idService:id Upstream du service internet du client
    direction: upstream ou downstream
    """

    if direction == "up":

        oid_max = "1.3.6.1.4.1.637.61.1.47.3.24.1.7." + str(
            idService)  # OntBandwidthProfileEIR: debit up max provionnée
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_max)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=50):
            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    Max = int(varBind[1].prettyPrint()) / 1000
        return str(int(Max)) + " Mo"

    else:
        oid_max = "1.3.6.1.4.1.637.61.1.47.3.19.1.8." + str(idService)  # OntShaperProfileEIR debit down max provisionné

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_max)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=50):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    Max = int(varBind[1].prettyPrint()) / 1000
            if Max <= 39:
                offre = "FIBRE BI"
                break
            elif Max > 39 and Max <= 59:
                offre = "FIBRE MAX"
                break
            elif Max > 59 and Max <= 99:
                offre = "FIRBE MEGA"
                break
            else:
                offre = "FIRBE MEGA PLUS"
                break

        return str(int(Max)) + " Mo", offre


def getProfileName(ip, idService, direction="down"):
    """
    Fonction permettant d'avoir le profile name du client
    provisionné selon le sens:
    Arguments:
    ip:@IP de l'OLT
    idService:id Upstream du service internet du client
    direction: upstream ou downstream """

    if direction == "up":
        oid_profileName = "1.3.6.1.4.1.637.61.1.47.3.24.1.2." + str(idService)  # OntBandwidthProfile: profile name
    else:
        oid_profileName = "1.3.6.1.4.1.637.61.1.47.3.19.1.2." + str(idService)  # OntBandwidthProfile: profile name

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('t1HAI2nai'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_profileName)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=50):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                profileName = str(varBind[1].prettyPrint())
    return profileName


def getProvisioning(serviceId):
    """ Fonction permettant d'obtenir le profile id du client
        Arguments:
        serviceId:numéro du client
        """
    date_start = datetime.datetime.now()
    # data = pd.read_csv(getpath(), sep=";", low_memory=False)
    data = data_inventaire(serviceId)

    # df0=pd.read_csv("input/inventaireEqmt_V0.csv",sep=";")
    # data=data.merge(df0[["ip","nomOlt"]],left_on="ip_olt",right_on="ip").drop(["ip"],axis=1)
    data["ontindex1"] = (data["slot"].astype(int) + 1) * (2 ** 25) + 14 * (2 ** 21) + (data["pon"].astype(int) - 1) * (
            2 ** 16) + (data["ont_id"].astype(int) - 1) * (2 ** 9)
    ontindex = data[data["serviceId"] == serviceId]['ontindex1'].values[0]
    ont_index = data[data["serviceId"] == serviceId]['ont_index'].values[0]
    ip = data[data["serviceId"] == serviceId]["ip_olt"].values[0]
    nomOlt = data[data["serviceId"] == serviceId]["nomOlt"].values[0]
    ont_id = data[data['serviceId'] == serviceId]['ont_id'].values[0]
    pon = data[data['serviceId'] == serviceId]['pon'].values[0]
    slot = data[data['serviceId'] == serviceId]['slot'].values[0]
    vendeur = data[data['serviceId'] == serviceId]['vendeur'].values[0]
    # print('ont_index', ont_index)
    # print('ontindex', ontindex)
    isAnomalie = True

    dataFibre = fiberCut(serviceId)
    dataOnt = ontPowerUnderLimit(serviceId)
    dataOlt = oltPowerUnderLimit(serviceId)
    dataPower = powerSupplyDown(serviceId)

    if (dataFibre['status'] == 'ok' and dataPower['status'] == 'ok' and dataOnt['status'] == 'ok' and dataOlt[
        'status'] == 'ok'):
        isAnomalie = False

    anomalie = {
        'fiberCut': dataFibre,
        'powerSupplyDown': dataPower,
        'ontUnderLimit': dataOnt,
        'oltPowerUnderLimit': dataOlt
    }
    anoFibre = ''
    anoONT = ''
    anoOLT = ''
    anoPower = ''
    if dataFibre['status'] == 'ko':
        anoFibre = dataFibre['anomalie'] + ", "

    if dataOnt['status'] == 'ko':
        anoONT = dataOnt['anomalie'] + ", "

    if dataOlt['status'] == 'ko':
        anoOLT = dataOlt['anomalie'] + ", "

    if dataPower['status'] == 'ko':
        anoPower = dataPower['anomalie']

    anomalies = "".join([anoFibre, anoONT, anoOLT, anoPower])
    # TODO : ce chargement est à revoir
    # if not isAnomalie:
    #     historique_diagnostic(serviceId, nomOlt, ip, vendeur, str(pon), str(slot), str(ont_id), "Pas d'anomalies",
    #                           isAnomalie)
    # else:
    #     historique_diagnostic(serviceId, nomOlt, ip, vendeur, str(pon), str(slot), str(ont_id), anomalies, isAnomalie)
    if vendeur == "Huawei":
        dataHuawei = configurationClientsHuawei(serviceId)

        return {
            # "ont_id": ont_id,
            "nomOLT": nomOlt,
            "ipOLT": ip,
            "pon": str(pon),
            "slot": str(slot),
            "ont": str(ont_id),
            "opticValue": getOpticalSignal(serviceId),
            "serviceId": str(serviceId),
            'hasAnomalie': isAnomalie,
            'anomalies': anomalie,
            "statutModem": dataHuawei.get('statutModem'),
            "qualitySignal": dataHuawei.get('qualitySignal'),
            "offre": dataHuawei.get('offre'),
            "maxUp": dataHuawei.get('MaxUp'),
            "maxDown": dataHuawei.get('MaxDown'),
        }
    id_services_up = []
    id_services_down = []
    listOperStatus = []

    # oid rx power ont
    oid_rxPower = "1.3.6.1.4.1.637.61.1.35.10.14.1.2" + "." + str(ont_index)

    # oid operstatus
    oid_operstatus = "1.3.6.1.2.1.2.2.1.8." + str(
        ontindex)  # str(ont_index) #Up(1),Down(2),Testing(3),Unknown(4),Dormant(5), notPresent(6),lowerLayerDown(7)

    # Upstream:
    oid_profileIdUp = "1.3.6.1.4.1.637.61.1.47.5.2.1.3." + str(
        ont_index)  # OntBandwidthProfileId: profile id == > 1st id oupput correspond to the id of internet, 6th id output to the VoIP

    # Downstream
    oid_profileIdDown = "1.3.6.1.4.1.637.61.1.47.5.1.1.4." + str(
        ont_index)  # OntShaperProfileId: profile id == > 1st id oupput coreespond to the id of internet

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('t1HAI2nai'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_operstatus)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=50):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                operstatus = varBind[1].prettyPrint()
                if operstatus == "1":
                    statut = "Actif"
                else:
                    statut = "Inactif"
                listOperStatus.append(statut)

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('t1HAI2nai'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_rxPower)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=50):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                rxPower = int(varBind[1].prettyPrint()) * 2 / 1000
                if int(varBind[1].prettyPrint()) == 32768:
                    qualitySignal = "Signal indisponible"
                elif rxPower <= -30:
                    qualitySignal = "Très dégradé"
                elif (rxPower > -30 and rxPower <= -27) or rxPower > 10:
                    qualitySignal = "Dégradé"
                else:
                    qualitySignal = "Normal"

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('t1HAI2nai'),
                              UdpTransportTarget(transportAddr=(ip, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid_profileIdUp)),
                              lexicographicMode=False,
                              lookupMib=False, timeout=2.0, retries=50):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                id_up = varBind[1].prettyPrint()
                # print('id_up : ', id_up)
                id_services_up.append(id_up)

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('t1HAI2nai'),
                              UdpTransportTarget(transportAddr=(ip, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid_profileIdDown)),
                              lexicographicMode=False,
                              lookupMib=False, timeout=2.0, retries=50):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                id_down = varBind[1].prettyPrint()
                id_services_down.append(id_down)
    # print('------------------recuperatons des données----------------')
    # print('Id_Serv', id_services_up)
    MaxUp = getMaxDebit(ip, id_services_up[0], direction="up")
    MaxDown, offre = getMaxDebit(ip, id_services_down[0], direction="down")
    profileNameUp = getProfileName(ip, id_services_up[0], direction="up")
    profileNameDown = getProfileName(ip, id_services_down[0], direction="down")

    # Transformation des valeurs maxUp et maxDown en int
    MaxUp = int(re.search(r'\d+', MaxUp).group())
    MaxDown = int(re.search(r'\d+', MaxDown).group())

    print(f'Numero: {serviceId}, Vendeur: {vendeur}, MaxUp: {MaxUp}, MaxDown: {MaxDown}, Statut: {statut}')

    # Inserer les donnes dans la table real_time_diagnostic
    con = connect()
    cursor = con.cursor()
    cursor.execute(''' INSERT INTO real_time_diagnostic (numero,vendeur, debit_up, debit_down, statut, date) 
                                    VALUES (%s, %s, %s, %s, %s, %s) ''',
                   (serviceId, vendeur, MaxUp, MaxDown, statut, dt.now()), )

    con.commit()
    print("Insertion is running.....")

    return {
        "idServiceUp": id_services_up[0],
        "idServiceDown": id_services_down[0],
        "statutModem": listOperStatus[0],
        "qualitySignal": qualitySignal,
        "maxUp": MaxUp,
        "maxDown": MaxDown,
        "profileNameUp": profileNameUp,
        "profileNameDown": profileNameDown,
        "nomOLT": nomOlt,
        "ipOLT": ip,
        "pon": str(pon),
        "slot": str(slot),
        "ont": str(ont_id),
        "opticValue": str(getOpticalSignal(serviceId)),
        "serviceId": str(serviceId),
        "offre": offre,
        'hasAnomalie': isAnomalie,
        'anomalies': anomalie
    }

# print(getProvisioning("338276153"))
