from pysnmp.hlapi import *
import datetime
import pandas as pd
from script.function import data_inventaire, data_invent, pathMaintenance


def oltPowerUnderLimit(serviceId):
    """
    fonction permettant de diagnostiquer si la puissance du signal
    reçue par l'olt de la part de l'ont est faible.
    Arguments:
         - serviceId: numéro de téléphone du client

    """

    df = data_inventaire(serviceId)

    index, ip, _ont_, vendeur, pon, slot = str(df[df['serviceId'] == serviceId]['ont_index'].values[0]), \
                                           str(df[df['serviceId'] == serviceId]['ip_olt'].values[0]), \
                                           str(df[df['serviceId'] == serviceId]['ont_id'].values[0]), \
                                           str(df[df['serviceId'] == serviceId]['vendeur'].values[0]), \
                                           str(df[df['serviceId'] == serviceId]['pon'].values[0]), \
                                           str(df[df['serviceId'] == serviceId]['slot'].values[0])

    if vendeur == "Huawei":

        oid_ont = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6" + "." + index + "." + _ont_  # oid de oltRxpower:1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6
        oid_olt = "1.3.6.1.4.1.2011.6.128.1.1.2.22.1.28" + "." + _ont_  # oid de sfpclass:1.3.6.1.4.1.2011.6.128.1.1.2.22.1.28
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ont)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    oltpower = varBind[1].prettyPrint()

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('OLT@osn_read'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_olt)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    sfpclass = varBind[1].prettyPrint()

        if int(oltpower) == 2147483647:
            return {
                'status': 'ko',
                "anomalie": "Puissance optique OLT indisponible",
                "etat": "Critique",
                "description": "Interruption du service",
                "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
                                   "Demander au technicien de faire une mesure de réflectometrie pour localisation du point de coupure."]
            }
        elif int(oltpower) != 2147483647:
            oltpower_dbm = (int(oltpower) - 10000) / 100
            if (sfpclass != "102" and oltpower_dbm <= -30):
                return {
                    'status': 'ko',
                    "anomalie": "Puissance optique OLT très faible",
                    "signal_optique": oltpower_dbm,
                    "etat": "Majeur",
                    "description": "Dégradation du signal optique",
                    "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
                                       "Demander au technicien de qualifier les differentes sections de la liaison pour identifier la cause de(s) la forte(s) attenuation(s) par mesures de puissance et de réflectomètrie"]
                }
            elif (sfpclass != "102" and ((oltpower_dbm > -30 and oltpower_dbm <= -27) or oltpower_dbm > 10)) or (
                    sfpclass == "102" and (
                    oltpower_dbm < -30 or oltpower_dbm > 10)):  # sfpclass=102 coreespond à sfpclass="CPLUS"
                return {
                    'status': 'ko',
                    "anomalie": "Puissance optique OLT faible",
                    "signal_optique": oltpower_dbm,
                    "etat": "Moyen",
                    "description": "Puissance optique admissible, pas forcément de dégradation de service",
                    "Recommandation": ["Voir dans l'historique si existant que l'anomalie était déjà présente",
                                       "Remonter à l'équipe intervention terrain si l'anomalie est persistante"]
                }
            else:
                return {'status': 'ok', 'description': 'Puissance signal ONT reçu par OLT OK',
                        'signal_optique': oltpower_dbm}

    elif vendeur == "Nokia":

        oid_ont = "1.3.6.1.4.1.637.61.1.35.10.18.1.2" + "." + index  # oid de oltRxpower pour Nokia:1.3.6.1.4.1.637.61.1.35.10.18.1.2
        slot_index = str(4352 + int(slot) + 1)
        oid_olt = "1.3.6.1.4.1.637.61.1.56.6.1.13" + "." + slot_index + "." + pon  # oid de sfpclass: 1.3.6.1.4.1.637.61.1.56.6.1.13

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_ont)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    oltpower = varBind[1].prettyPrint()

        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in getCmd(SnmpEngine(),
                                 CommunityData('t1HAI2nai'),
                                 UdpTransportTarget(transportAddr=(ip, 161)),
                                 ContextData(),
                                 ObjectType(ObjectIdentity(oid_olt)),
                                 lexicographicMode=False,
                                 lookupMib=False, timeout=2.0, retries=150):

            if errorIndication:
                raise Exception('SNMP getCmd error {0}'.format(errorIndication))
            else:
                for varBind in varBinds:
                    sfpclass = varBind[1].prettyPrint()

        if int(oltpower) == 32768:
            return {
                'status': 'ko',
                "anomalie": "Puissance optique OLT indisponible",
                "etat": "Critique",
                "description": "Interruption du service",
                "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
                                   "Demander au technicien de faire une mesure de réflectometrie pour localisation du point de coupure."]
            }
        elif int(oltpower) != 32768:
            oltpower_dbm = int(oltpower) / 10
            if (sfpclass in ["7", "8"] and oltpower_dbm <= -30):
                return {
                    'status': 'ko',
                    "anomalie": "Puissance optique OLT très faible",
                    "signal_optique": oltpower_dbm,
                    "etat": "Majeur",
                    "description": "Dégradation du signal optique",
                    "Description": "Dégradation du signal optique",
                    "Recommandation": ["Remonter l'anomalie à l'équipe intervention terrain",
                                       "Demander au technicien de qualifier les differentes sections de la liaison pour identifier la cause de(s) la forte(s) attenuation(s) par mesures de puissance et de réflectomètrie"]
                }
            elif (sfpclass in ["7", "8"] and ((oltpower_dbm > -30 and oltpower_dbm <= -27) or oltpower_dbm > 10)):
                return {
                    'status': 'ko',
                    "anomalie": "Puissance optique OLT faible",
                    "signal_optique": oltpower_dbm,
                    "etat": "Moyen",
                    "description": "Puissance optique admissible, pas forcément de dégradation de service",
                    "Recommandation": ["Voir dans l'historique si existant que l'anomalie était déjà présente",
                                       "Remonter à l'équipe intervention terrain si l'anomalie est persistante"]
                }
            else:
                return {'status': 'ok', 'description': 'Puissance signal ONT reçu par OLT OK',
                        'signal_optique': oltpower_dbm}


if __name__ == "__main__":
    start_time = datetime.now()
    print(oltPowerUnderLimit('338200128'))
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


def scriptMaintenanceOltPwr(taille, pas, numFile):
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
            data = oltPowerUnderLimit(serviceId)
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
        except:
            pass
    df = pd.DataFrame(
        zip(listNumero, listOlt, listPon, listSlot, listIpOlt, listVendeur, listAnomalie, listEtat),
        columns=['NUMERO', 'NOM_OLT', 'PON', 'SLOT', 'IP', 'VENDEUR', 'ANOMALIE', 'CRITICITE'])
    filename = pathMaintenance() + "olt_ftth_" + str(numFile) + ".csv"
    df.to_csv(filename, sep=";", index=False)
    end_time = datetime.now()
    print(str(numFile), 'Duration: {}'.format(end_time - start_time))
