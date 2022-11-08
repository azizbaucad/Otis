import os
import yact
import yaml
from flask import Config, jsonify, request
import psycopg2
import pandas as pd



class YactConfig(Config):
    def from_yaml(self, config_file, directory=None):
        config = yact.from_file(config_file, directory=directory)
        for section in config.sections:
            self[section.upper()] = config[section]

# fonction configuration
def configuration():
    with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
        cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)
        return cfg

# fonction add_headers
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    return response

#fonction error
def error(message):
    return jsonify({
        'success': False,
        'message': message
    })

# fonction de connection à la BDD
def connect():
    return psycopg2.connect(database=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)

# fonction pour les requetes de type select sans arguments
def select_query(query):
    con = None
    try:
        con = connect()
        df = pd.read_sql(query, con)
        data = df.to_dict(orient='records')
        con.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return data

def select_query_argument(query, numero=None):
    con = None
    #numero = request.args.get('numero')
    #where_clause = f'{str(argument)}'
    if numero is not None or numero == "":
        try:
            con = connect()
            df = pd.read_sql(query.format(numero), con)
            data = df.to_dict(orient='records')
            con.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()
        return data
    else:
        return {"message": "la fonction manque un argument : numero"}

# fonction select avec plusieurs arguments
def select_query_date_between(query, arg1=None, arg2=None, arg3=None):
    if arg1 is not None or arg1 == "" or arg2 is not None or arg2 == "":
        try:
            #duree = arg2 - arg1
            con = connect()
            df = pd.read_sql(query.format(arg1, arg2, arg3), con)
            data = df.to_dict(orient='records')
            con.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()
        return data
    else:
        return {"Error": "Verifier les arguments entrées !!!"}



# test des parmas
# if __name__ == '__main__':
#     print("-----------------test mes codes-----------------------")
#     def testclearg(query, *args):
#         print(".....The query is....................\n")
#         print(query)
#         print("\n ........ The arguments is .........")
#         for i in args:
#             print(i)
#
#
#     a1 = "Bob"
#     a2 = [1, 2, 3]
#     a3 = {'a': 222, 'b': 333, 'c': 444}
#     testclearg("Select * from Something", a1, a2, a3)


    #testclearg(a1, a2, a3, param1=True, param2=12, param3=None)


NAME_DB = configuration()["NAME_DB"]
USER_DB = configuration()["USER_DB"]
PASSWORD_DB = configuration()["PASSWORD_DB"]
HOST_DB = configuration()["HOST_DB"]
PORT_DB = configuration()["PORT_DB"]
