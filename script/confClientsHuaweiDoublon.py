from pysnmp.hlapi import *


def getConfClientsHuawei(ip, _ont_, pon, slot):
    """ 
    fonction permettant d'avoir la configuration du client Huawei: offre,débits maxi up et down
    
    Arguments:
    - serviceId: numero du client
    - index: UNI du client
    - ip: adresse IP de l'OLT
    - _ont_: id ont du client
    - pon : pon id du client
    - slot : slot du client
    """

    shelf = 0

    listindex1 = []
    listindex2 = []
    listindex3 = []
    listindex4 = []
    listindex5 = []

    oid1 = "1.3.6.1.4.1.2011.5.14.5.2.1.5"
    oid2 = "1.3.6.1.4.1.2011.5.14.5.2.1.4"
    oid3 = "1.3.6.1.4.1.2011.5.14.5.2.1.3"
    oid4 = "1.3.6.1.4.1.2011.5.14.5.2.1.2"
    oid5 = "1.3.6.1.4.1.2011.5.14.5.2.1.8"

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('OLT@osn_read'),
                              UdpTransportTarget(transportAddr=(ip, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid1)),
                              lexicographicMode=False,
                              lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                if str(varBind[1].prettyPrint()) == str(_ont_):
                    listindex1.append(varBind[0].prettyPrint().split(".")[-1])
                else:
                    pass

    for idx1 in listindex1:
        oid = oid2 + "." + idx1
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=5):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    if str(varBind[1].prettyPrint()) == str(pon):
                        listindex2.append(varBind[0].prettyPrint().split(".")[-1])

    for idx2 in listindex2:

        oid = oid3 + "." + idx2
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=5):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    if str(varBind[1].prettyPrint()) == str(slot):
                        listindex3.append(varBind[0].prettyPrint().split(".")[-1])

    for idx3 in listindex3:

        oid = oid4 + "." + idx3
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=5):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    if str(varBind[1].prettyPrint()) == str(shelf):
                        listindex4.append(varBind[0].prettyPrint().split(".")[-1])

    for idx4 in listindex4:
        oid = oid5 + "." + idx4
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=5):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    if str(varBind[1].prettyPrint()) == str(45):
                        listindex5.append(varBind[0].prettyPrint().split(".")[-1])

    oid_up = "1.3.6.1.4.1.2011.5.14.5.2.1.21" + "." + listindex5[0]  # downstream
    oid_down = "1.3.6.1.4.1.2011.5.14.5.2.1.22" + "." + listindex5[0]  # upstream

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_up)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                down_str = varBind[1].prettyPrint()

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData('OLT@osn_read'),
                             UdpTransportTarget(transportAddr=(ip, 161)),
                             ContextData(),
                             ObjectType(ObjectIdentity(oid_down)),
                             lexicographicMode=False,
                             lookupMib=False, timeout=2.0, retries=5):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                up_str = varBind[1].prettyPrint()

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
            for varBind in varBinds:
                if varBind[1].prettyPrint() == down_str:
                    id_dwstr = varBind[0].prettyPrint().split(".")[-1]
                elif varBind[1].prettyPrint() == up_str:
                    id_upstr = varBind[0].prettyPrint().split(".")[-1]
                else:
                    pass

    oid_debit_up = "1.3.6.1.4.1.2011.5.14.3.8.1.5" + "." + id_upstr
    oid_debit_down = "1.3.6.1.4.1.2011.5.14.3.8.1.5" + "." + id_dwstr

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
                    break
                elif debit_down > 39 and debit_down <= 59:
                    offre = "FIBRE MAX"
                    break
                elif debit_down > 59 and debit_down <= 99:
                    offre = "FIRBE MEGA"
                    break
                else:
                    offre = "FIRBE MEGA PLUS"
                    break
    return {"offre": offre,
            "MaxUp": debit_up,
            "MaxDown": debit_down,
            }


# print(getConfClientsHuawei('10.155.14.50', 15, 2, 8))
