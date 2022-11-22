from pysnmp.hlapi import *
import datetime
from script.function import data_inventaire


def getOpticalSignal(serviceId):
    """ 
    fonction permettant d'avoir la puissance du signal
    reçue par l'olt de la part de l'ont .
    Arguments:
         - serviceId: numéro de téléphone du client
         
    """
    df = data_inventaire(serviceId)
    index, _ont_, vendeur, ip = str(df[df['serviceId'] == serviceId]['ont_index'].values[0]), \
                                str(df[df['serviceId'] == serviceId]['ont_id'].values[0]), \
                                str(df[df['serviceId'] == serviceId]['vendeur'].values[0]), \
                                str(df[df['serviceId'] == serviceId]['ip_olt'].values[0])

    if vendeur == "Huawei":

        oid_ont = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4" + "." + index + "." + _ont_  # oid de ontRxpower:1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ont)),
                                 lexicographicMode=False,
                                 lookupMib=False):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    ontpower = varBind[1].prettyPrint()
                    ontpower_dbm = int(ontpower) / 100

        # return ontpower_dbm
        return ontpower_dbm if ontpower_dbm < 20000 else 0


    elif vendeur == "Nokia":

        oid_ont = "1.3.6.1.4.1.637.61.1.35.10.14.1.2" + "." + index  # oid de ontRxpower pour Nokia:1.3.6.1.4.1.637.61.1.35.10.18.1.2
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ont)),
                                 lexicographicMode=False,
                                 lookupMib=False):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    ontpower = varBind[1].prettyPrint()
                    ontpower_dbm = int(ontpower) * 2 / 1000

            # return ontpower_dbm
            return ontpower_dbm if ontpower_dbm < 60 else 0


if __name__ == "__main__":
    start_time = datetime.now()
    print(getOpticalSignal("338270038"))
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
