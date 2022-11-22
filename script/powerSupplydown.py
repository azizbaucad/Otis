import csv
from pysnmp.hlapi import *
import datetime
from script.function import data_inventaire, data_invent, pathMaintenance

def powerSupplyDown(serviceId):
    data = data_inventaire(serviceId)
    ont_index = data[data["serviceId"] == serviceId]["ont_index"].values[0]
    ip = data[data["serviceId"] == serviceId]["ip_olt"].values[0]
    ont_id = data[data["serviceId"] == serviceId]['ont_id'].values[0]
    data["ponindex1"] = (data["slot"].astype(int) + 1) * (2 ** 25) + 13 * (2 ** 21) + (data["pon"].astype(int) - 1) * (
            2 ** 16)
    ponindex = data[data["serviceId"] == serviceId]['ponindex1'].values[0]
    vendeur = data[data["serviceId"] == serviceId]['vendeur'].values[0]

    if vendeur == "Huawei":

        oid_operstatus = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15." + str(ont_index) + "." + str(
            ont_id)  # Up(1),Down(2),Unknown(-1)
        oid_ontrowstatus = "1.3.6.1.4.1.2011.6.128.1.1.2.43.1.10." + str(ont_index) + "." + str(
            ont_id)  # Active(1), NotInService(2), NotReady(3), CreateAndGo(4), CreateAndWait(5), Destroy(6)
        oid_ranging = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.20." + str(ont_index) + "." + str(
            ont_id)  # Not Ranged(-1), Ranged(>0)
        oid_lastdowncause = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.24." + str(ont_index) + "." + str(
            ont_id)  # Loss of signal(1),Loss of signal for ONUi or Loss of burst for ONUi(2),Loss of frame of ONUi(3),Signal fail of ONUi(4),Loss of acknowledge with ONUi(5),Loss of PLOAM for ONUi(6),Deactive ONT fails(7),Deactive ONT success(8),Reset ONT(9),Re-register ONT(10),Pop up fail(11),Dying-gasp(13),Loss of key synch with ONUi(15),Deactived ONT due to the ring(18),Shut down ONT optical module(30),Reset ONT by ONT command(31),Reset ONT by ONT reset button(32),Reset ONT by ONT software(33),Deactived ONT due to broadcast attack(34),Unknown(-1)
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ontrowstatus)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    rowStatus = varBind[1].prettyPrint()

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_operstatus)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    operStatus = varBind[1].prettyPrint()

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ranging)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    ranging = varBind[1].prettyPrint()

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_lastdowncause)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    currentAlarm = varBind[1].prettyPrint()

        if rowStatus == "1" and operStatus == "2" and ranging == "-1" and currentAlarm == "13":
            return {
                'status': 'ko',
                "anomalie": "Modem éteint",
                "etat": "Critique",
                "description": "Défaut d'alimentation électrique",
                "Recommandation": ["Demander au client de vérifier si le modem est bien alimenté électriquement"]
            }
        else:
            return {'status': 'ok', 'description': 'Pas de defaut alimentation electrique'}


    elif vendeur == "Nokia":

        currentAlarmList = []
        oid_operstatus = "1.3.6.1.2.1.2.2.1.8." + str(
            ont_index)  # Up(1),Down(2),Testing(3),Unknown(4),Dormant(5), notPresent(6),lowerLayerDown(7)
        oid_ontrowstatus = "1.3.6.1.4.1.637.61.1.35.10.1.1.2." + str(
            ont_index)  # ontRowStatus:Active(1),NotInService(2),NotReady(3),CreateAndGo(4),CreateAndWait(5),Destroy(6)
        oid_ranging = "1.3.6.1.4.1.637.61.1.35.11.4.1.5." + str(ponindex) + "." + str(ont_id)
        oid_currentAlarms = "1.3.6.1.4.1.637.61.1.35.10.4.1.2." + str(ont_index)
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ontrowstatus)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    rowStatus = varBind[1].prettyPrint()
                    # print("rowstatus",rowStatus)

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_operstatus)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    operStatus = varBind[1].prettyPrint()
                    # print("operStatus",rowStatus)

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ranging)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    ranging = varBind[1].prettyPrint()
                    # print("ranging",rowStatus)

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_currentAlarms)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    temp_ = bin(int(varBind[1].prettyPrint()))[::-1][:-2]
                    for i in range(len(temp_)):
                        if temp_[i] == "1":
                            currentAlarmList.append(str(i + 1))
                for i in currentAlarmList:
                    if i == "18":
                        currentAlarm = "18"
                    # print("currentAlarm",rowStatus)

        if rowStatus == "1" and operStatus != "1" and ranging != "1" and currentAlarm == "18":
            return {
                'status': 'ko',
                "anomalie": "Modem éteint",
                "etat": "Critique",
                "description": "Défaut d'alimentation électrique",
                "recommandation": [
                    "Demander au client de vérifier si le modem est bien alimenté électriquement"]
            }
        else:
            return {'status': 'ok', 'description': 'Pas de defaut alimentation electrique'}


##print(powerSupplyDown("338680206"))

def scriptMaintenancePwrSupplyDown():
    df = data_invent()
    size = len(df.index)
    with open(pathMaintenance() + "file_power" + datetime.today().strftime('%Y%m%d%H%M%S') + ".csv", 'w',
              newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['serviceId', 'pon', 'ip_olt', 'anomalie', 'etat'])

        for i in range(size):
            serviceId = df['serviceId'].values[i]
            pon = df['ponIndex'].values[i]
            ip_olt = df['ip_olt'].values[i]
            print(i)
            print(serviceId)
            if serviceId != '338253791' and serviceId != '338253542':
                status = powerSupplyDown(serviceId)['status']
                if powerSupplyDown(serviceId)['status'] == 'ko':
                    etat = powerSupplyDown(serviceId)['etat']
                    message = powerSupplyDown(serviceId)['description']
                    print(message)
                    writer.writerow([serviceId, pon, ip_olt, message, etat])


if __name__ == "__main__":
    start_time = datetime.now()
    print(powerSupplyDown("338200128"))
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))