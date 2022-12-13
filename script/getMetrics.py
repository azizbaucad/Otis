import numpy as np
from pysnmp.hlapi import *
from datetime import datetime
from function import *
from script.confClientsNokia import *


def metrics(taille, pas):
    data = data_invent()
    m = data.apply(lambda x: str(x['serviceId']).startswith(('338', '339')),
                   axis=1)
    df = data[m]
    df = df[taille:(taille + pas)]
    listNumber = list(np.unique(df.serviceId))
    ontpowerList = []
    ontNumberList = []
    ontpowerListOlt = []
    listDate = []
    listVendeur = []
    start_time = datetime.now()
    i = 1
    for numero in listNumber:
        try:
            print(i)
            ontNumberList.append(numero)
            #listDate.append(datetime.today().strftime('%Y-%m-%d'))
            listDate.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            index, ip, _ont_, vendeur, pon, slot = str(df[df['serviceId'] == numero]['ont_index'].values[0]), \
                                                   str(df[df['serviceId'] == numero]['ip_olt'].values[0]), \
                                                   str(df[df['serviceId'] == numero]['ont_id'].values[0]), \
                                                   str(df[df['serviceId'] == numero]['vendeur'].values[0]), \
                                                   str(df[df['serviceId'] == numero]['pon'].values[0]), \
                                                   str(df[df['serviceId'] == numero]['slot'].values[0])
            listVendeur.append(vendeur)

            if vendeur == "Huawei":

                print("Vendeur Huawei")

                ponIndex = 125 * (2 ** 25) + 0 * (2 ** 19) + int(slot) * (2 ** 13) + int(pon) * (
                        2 ** 8)  # calcul du pon index
                oid_Rx = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4" + "." + index + "." + _ont_  # oid de ontRxpower:1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4
                oid_Tx = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.3" + "." + index + "." + _ont_  # oid de ontTxpower:1.3.6.1.4.1.2011.6.128.1.1.2.51.1.3
                oid_olt_Rx = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6" + "." + str(ponIndex) + "." + str(_ont_)

                # oid de OltRxpower:1.3.6.1.4.1.2011.6.128.1.1.2.23.1.4
                # oid_olt_Tx = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6" + "." + str(
                #     ponIndex) + "." + _ont_  # oid de OltTxpower:1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6



                for (errorIndication,
                     errorStatus,
                     errorIndex,
                     varBinds) in getCmd(SnmpEngine(),
                                         CommunityData('OLT@osn_read'),
                                         UdpTransportTarget(transportAddr=(ip, 161)),
                                         ContextData(),
                                         ObjectType(ObjectIdentity(oid_Rx)),
                                         lexicographicMode=False,
                                         lookupMib=False, timeout=2.0, retries=20):
                    if errorIndication:
                        raise Exception('SNMP getCmd error {0}'.format(errorIndication))
                    else:

                        for varBind in varBinds:
                            ontpower = varBind[1].prettyPrint()
                            if int(ontpower) == 2147483647:
                                ontpower_dbm = 0
                                ontpowerList.append(ontpower_dbm)
                            else:
                                ontpower_dbm = int(ontpower) / 100
                                ontpowerList.append(ontpower_dbm)

                for (errorIndication,
                     errorStatus,
                     errorIndex,
                     varBinds) in getCmd(SnmpEngine(),
                                         CommunityData('OLT@osn_read'),
                                         UdpTransportTarget(transportAddr=(ip, 161)),
                                         ContextData(),
                                         ObjectType(ObjectIdentity(oid_olt_Rx)),
                                         lexicographicMode=False,
                                         lookupMib=False, timeout=2.0, retries=20):
                    if errorIndication:
                        raise Exception('SNMP getCmd error {0}'.format(errorIndication))
                    else:
                        for varBind in varBinds:
                            ontpowerOlt = varBind[1].prettyPrint()
                            if int(ontpowerOlt) == 2147483647:
                                ontpower_dbm_Olt = 0
                                ontpowerListOlt.append(ontpower_dbm_Olt)
                            else:
                                ontpower_dbm_Olt = (int(ontpowerOlt) - 1000) / 100
                                ontpowerListOlt.append(ontpower_dbm_Olt)

            elif vendeur == "Nokia":

                print('Vendeur Nokia')

                df["ponindex1"] = (df["slot"] + 1) * (2 ** 25) + 13 * (2 ** 21) + (df["pon"] - 1) * (2 ** 16)
                ponIndex = df[df["serviceId"] == numero]['ponindex1'].values[0]

                oid_Rx = "1.3.6.1.4.1.637.61.1.35.10.14.1.2" + "." + index  # oid de ontRxpower pour Nokia:1.3.6.1.4.1.637.61.1.35.10.18.1.2
                oid_Tx = "1.3.6.1.4.1.637.61.1.35.10.14.1.4" + "." + index  # oide de Tx power au niveau de l'equipement du client
                oid_olt_Tx = "1.3.6.1.4.1.637.61.1.35.11.9.1.2" + "." + str(
                    ponIndex)  # oide de Tx power au niveau de l'olt abritant le client
                oid_olt_Rx = "1.3.6.1.4.1.637.61.1.35.10.18.1.2" + "." + index  # oid de OltRxpower Ok

                for (errorIndication,
                     errorStatus,
                     errorIndex,
                     varBinds) in getCmd(SnmpEngine(),
                                         CommunityData('t1HAI2nai'),
                                         UdpTransportTarget(transportAddr=(ip, 161)),
                                         ContextData(),
                                         ObjectType(ObjectIdentity(oid_Rx)),
                                         lexicographicMode=False,
                                         lookupMib=False, timeout=2.0, retries=20):

                    if errorIndication:
                        raise Exception('SNMP getCmd error {0}'.format(errorIndication))
                    else:
                        for varBind in varBinds:
                            ontpower = varBind[1].prettyPrint()
                            if int(ontpower) == 32768:
                                ontpower_dbm = 0
                                ontpowerList.append(ontpower_dbm)
                            else:
                                ontpower_dbm = int(ontpower) * 2 / 1000
                                ontpowerList.append(ontpower_dbm)

                for (errorIndication,
                     errorStatus,
                     errorIndex,
                     varBinds) in getCmd(SnmpEngine(),
                                         CommunityData('t1HAI2nai'),
                                         UdpTransportTarget(transportAddr=(ip, 161)),
                                         ContextData(),
                                         ObjectType(ObjectIdentity(oid_olt_Rx)),
                                         lexicographicMode=False,
                                         lookupMib=False, timeout=2.0, retries=20):

                    if errorIndication:
                        raise Exception('SNMP getCmd error {0}'.format(errorIndication))
                    else:

                        for varBind in varBinds:
                            ontpowerOlt = varBind[1].prettyPrint()
                            if int(ontpowerOlt) == 65534:
                                ontpower_dbm_Olt = 0
                                ontpowerListOlt.append(ontpower_dbm_Olt)
                            else:
                                ontpower_dbm_Olt = int(ontpowerOlt) / 10
                                ontpowerListOlt.append(ontpower_dbm_Olt)
            i += 1
        except:
            #number_except_metric(numero)
            pass

    df1 = pd.DataFrame(zip(ontNumberList, ontpowerListOlt, ontpowerList, listDate, listVendeur),
                       columns=['numero', 'oltrxpwr', 'ontrxpwr', 'date', 'Vendeur'])
    print(df1)
    #metric_to_database(df1)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

if __name__ == '__main__':
    print(metrics(1,8))
