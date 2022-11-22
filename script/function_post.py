from script.function import  *
from flask import Flask, request, jsonify, Config
import json
import jsonpickle
import pandas as pd

# @app.route('/auth', methods=['POST'])
#def get_historique():
# TODO : Control username et password
def get_historique_by_date():
    data = request.get_json()
    date = data['date'],

    ret = {
         'numero': "77777777",
        "response": "ok",
        "code": 200
    }

    return jsonify(ret)
# get_historique
def get_historique():
    #data = []
    dat = []
    data = pd.DataFrame()
    con = None
    #data = request.get_json()
    #date = data['date']
    try:
        con = connect()
        cur = con.cursor()
        # cur.execute("Select numero, date_, created_at from historique_diagnostic where anomalie like '%Coupure%' and (NOW()::date  -  date_) >= 30 ;")
        # data = cur.fetchall()
        # for row in data:
        #     numero = row[1]
        #     #return row[1]
        # cur.close()
        # con.commit()
        #return jsonpickle.encode(data)
        query = "Select numero, date_, created_at from historique_diagnostic where anomalie like '%Coupure%' and (NOW()::date  -  date_) >= 30 ;"
        data_ = pd.read_sql(query, con)
        print(data_)
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    js = data_.to_dict(orient='records')
    ret = js
    return ret
