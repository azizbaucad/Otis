# Pour Nokia

from pysnmp.hlapi import *

from confClientsHuaweiDoublon import getConfClientsHuawei
from fiberCutDoublons import fiberCut
from function import *
from getSignalOpticalDoublons import getOpticalSignal
from oltPowerUnderLimitDoublons import oltPowerUnderLimit
from ontUnderLimitDoublons import ontPowerUnderLimit
from powerSupplydownDoublons import powerSupplyDown


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
                                 lookupMib=False, timeout=2.0, retries=5):
            if errorIndication:
                return {'error': 'SNMP getCmd error {0}'.format(errorIndication)}
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
                                 lookupMib=False, timeout=2.0, retries=5):

            if errorIndication:
                return {'error': 'SNMP getCmd error {0}'.format(errorIndication)}
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
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            return {'error': 'SNMP getCmd error {0}'.format(errorIndication)}
        else:
            for varBind in varBinds:
                profileName = str(varBind[1].prettyPrint())
    return profileName


def getProvisioningDoublons(ont_index, ip, ont_id, pon, slot, nomOlt, vendeur, serviceId):
    """ Fonction permettant d'obtenir le profile id du client
        Arguments:
        serviceId:numéro du client
        """

    # data=pd.read_csv("/Users/diouf028323/Documents/DBM/git/diagnosticdistantftth/script/output/inventaireglobal_ftth.csv",sep=";",low_memory=False)
    # df0=pd.read_csv("input/inventaireEqmt_V0.csv",sep=";")
    # data=data.merge(df0[["ip","nomOlt"]],left_on="ip_olt",right_on="ip").drop(["ip"],axis=1)
    # data["ontindex1"]=(data["slot"]+1) * (2**25) + 14 * (2**21 )+(data["pon"]-1) * (2**16)+(data["ont_id"]-1) * (2**9)
    ontindex = (int(slot) + 1) * (2 ** 25) + 14 * (2 ** 21) + (int(pon) - 1) * (2 ** 16) + (int(ont_id) - 1) * (
            2 ** 9)  # data[data["serviceId"]==serviceId]['ontindex1'].values[0]
    # ont_index=data[data["serviceId"]==serviceId]['ont_index'].values[0]
    # ip=data[data["serviceId"]==serviceId]["ip_olt"].values[0]
    # nomOlt=data[data["serviceId"]==serviceId]["nomOlt"].values[0]
    # ont_id=data[data['serviceId']==serviceId]['ont_id'].values[0]
    # pon=data[data['serviceId']==serviceId]['pon'].values[0]
    # slot=data[data['serviceId']==serviceId]['slot'].values[0]

    id_services_up = []
    id_services_down = []
    listOperStatus = []

    # oid rx power ont
    oid_rxPower = "1.3.6.1.4.1.637.61.1.35.10.14.1.2" + "." + str(ont_index)

    # oid operstatus
    oid_operstatus = "1.3.6.1.2.1.2.2.1.8." + str(ontindex)
    # str(ont_index) #Up(1),Down(2),Testing(3),Unknown(4),Dormant(5), notPresent(6),lowerLayerDown(7)

    # Upstream:
    oid_profileIdUp = "1.3.6.1.4.1.637.61.1.47.5.2.1.3." + str(ont_index)
    # OntBandwidthProfileId: profile id == > 1st id oupput coreespond to the id of internet, 6th id output to the VoIP

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
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            return {'error1': 'SNMP getCmd error {0}'.format(errorIndication), 'isCorrect': False}
        else:
            for varBind in varBinds:
                operstatus = varBind[1].prettyPrint()
                if operstatus == "1":
                    statut = "Actif"
                else:
                    statut = "Non Actif"
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
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            return {'error2': 'SNMP getCmd error {0}'.format(errorIndication), 'isCorrect': False}
        else:
            for varBind in varBinds:
                rxPower_1 = int(varBind[1].prettyPrint())
                rxPower = rxPower_1 * 2 / 1000

                print('rxPower1',rxPower_1)
                print('rxPower', rxPower)
                if rxPower_1 == 32768:
                    qualitySignal = "Signal indisponible"
                elif rxPower <= -30:
                    qualitySignal = "Très dégradé"
                elif ((rxPower > -30 and rxPower <= -27) or rxPower > 10):
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
                              lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            return {'error3': 'SNMP getCmd error {0}'.format(errorIndication), 'isCorrect': False}
        else:
            for varBind in varBinds:
                id_up = varBind[1].prettyPrint()
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
                              lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            return {'error4': 'SNMP getCmd error {0}'.format(errorIndication), 'isCorrect': False}
        else:
            for varBind in varBinds:
                id_down = varBind[1].prettyPrint()
                id_services_down.append(id_down)

    MaxUp = getMaxDebit(ip, id_services_up[0], direction="up")
    MaxDown, offre = getMaxDebit(ip, id_services_down[0], direction="down")
    profileNameUp = getProfileName(ip, id_services_up[0], direction="up")
    profileNameDown = getProfileName(ip, id_services_down[0], direction="down")

    isAnomalie = True

    dataFibre = fiberCut(ont_index, ip, ont_id, vendeur)
    dataOnt = ontPowerUnderLimit(ont_index, ip, ont_id, pon, slot, vendeur)
    dataOlt = oltPowerUnderLimit(ont_index, ip, ont_id, pon, slot, vendeur)
    dataPower = powerSupplyDown(ont_index, ip, ont_id, pon, slot, vendeur)

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

    if not isAnomalie:
        historique_diagnostic(serviceId, nomOlt, ip, vendeur, str(pon), str(slot), str(ont_id), "Pas d'anomalies",
                              isAnomalie)
    else:
        historique_diagnostic(serviceId, nomOlt, ip, vendeur, str(pon), str(slot), str(ont_id), anomalies, isAnomalie)
    if vendeur == "Huawei":
        return {
            "idServiceUp": id_services_up[0],
            "idServiceDown": id_services_down[0],
            "statutModem": listOperStatus[0],
            "qualitySignal": qualitySignal,
            "maxUp": getConfClientsHuawei(ip, ont_index, pon, slot)['MaxUp'],
            "maxDown": getConfClientsHuawei(ip, ont_index, pon, slot)['MaxDown'],
            "profileNameUp": profileNameUp,
            "profileNameDown": profileNameDown,
            "nomOLT": nomOlt,
            "ipOLT": ip,
            "pon": str(pon),
            "slot": str(slot),
            "ont": str(ont_id),
            "opticValue": str(getOpticalSignal(ont_index, ip, ont_id, vendeur)),
            "serviceId": str(serviceId),
            "offre": getConfClientsHuawei(ip, ont_index, pon, slot)['offre'],
            'hasAnomalie': isAnomalie,
            'anomalies': anomalie,
            'isCorrect': True
        }

    return {
        "ont_id": ont_id,
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
        "opticValue": str(getOpticalSignal(ont_index, ip, ont_id, vendeur)),
        "serviceId": str(serviceId),
        "offre": offre,
        'hasAnomalie': isAnomalie,
        'anomalies': anomalie,
        'isCorrect': True
    }


# 67109632; 2; 338243660 ; 10.155.71.14 ; 1 ; 1 ; 94371840 ; Nokia ; OLT-SIEGE-1
# print(getProvisioningDoublons(67109632, '10.155.71.14', 2, 1, 1, 'OLT-SIEGE-1', 'Nokia', 338243660))

if __name__ == "__main__":
    start_time = datetime.now()
    # def getProvisioningDoublons(ont_index, ip, ont_id, pon, slot, nomOlt, vendeur, serviceId):
    # print(getProvisioningDoublons('302916832', '10.155.28.38', 19, 15, 8, 'OLT-ALM-1', 'Nokia', 338200800))
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
