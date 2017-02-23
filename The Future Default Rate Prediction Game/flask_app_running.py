# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify
import pandas.io.sql as sql
import sqlite3
import platform

######
# USEFULL CODE FOR MIGRATING FROM WINDOWS to LINUX (example to PYTHONANYWHERE) - START
######
is_windows = any(platform.win32_ver())
if is_windows:
    print "windows"
    FULLPATH ="D:\\FlaskBasico\\EX2_API_WITH_FLASK_BOOTSTRAP\\"
else:
    print "linux"
    FULLPATH ='/home/EJCIFF2017/EX2_API_WITH_FLASK_BOOTSTRAP/'
######
# USEFULL CODE FOR MIGRATING FROM WINDOWS to LINUX (PYTHONANYWHERE) - END
######


######
# DATABASE - START, here it is only used for user data, but it can be used for anything.
######
connres = sqlite3.connect(FULLPATH+'configuration.db', check_same_thread=False)
cursorres = connres.cursor()
cursorres.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, coursekeyword TEXT, name TEXT, email TEXT, username TEXT, password TEXT)''')
connres.commit()
######
# DATABASE - END
######


######
# GLOBAL VARIABLE FOR SESSION - START
######
USER_SESSION = {}
USER_SESSION["USER"]= "none"
######
# GLOBAL VARIABLE FOR SESSION - END
######


######
# FLASK - START
######
app = Flask(__name__) # instancing the Flask object

#In Windows use "localhost" in your browser, what is equivalent to http://localhost:80/, which is also equivalent to http://127.0.0.1:80/
# http means your data will be tranfered using Hypertext Transfer Protocol, most commonly used over the internet
# localhost is a domain name system (DNS) which is equivalent to say 127.0.0.1, in other word "localhost" resolves to 127.0.0.1
# 80, means you will use the internet default port

#In pythonanywhere we will use http://<YOUR USER>.pythonanywhere.com, my one for the viedo is: http://rating.pythonanywhere.com



#Setting a route for python function called index, / is equivalent to "no route"
#This route is is widelly as Index or Home Page.
#@app.route('/') is equivalent to @app.route('/', methods=['GET', 'POST']), meaning GET and POST methods are allowed.
@app.route('/')
def index():
    return render_template('index.html',userlogged="Hei visitor, pss, you should log in before they catch ya!")

#Setting a route for python function called user(), now http://localhost:80/user (OR http://<YOUR USER>.pythonanywhere.com/user) will call this python function
#For simplicity, GET means that only URL like calls are allowed.
@app.route('/users', methods=['GET'])
def users():
    userdata = sql.read_sql('select * from users', connres)
    return userdata.to_json()



#Setting a route for python function called createuser(), now http://localhost:80/createuser (OR http://<YOUR USER>.pythonanywhere.com/createuser) will call this python function
# POST means it can only be called by a "form", for simplicity, it means web page form or a software must call this function, and calling it directly in the browser like "http://localhost:80/createuser" will not work because it is not allowed.
@app.route('/createuser', methods=['POST'])
def createuser():
    global USER_SESSION, connres, cursorres
#    print request.form#['name']
    if request.form['coursekeyword'] in ['BIGDATA', 'BIG DATA']:
        try:

#            print "CREATE USER 0.1"
            df_users = sql.read_sql("select username from users", connres)
#            print "CREATE USER 0.2"
            if sum(df_users['username'] == request.form['username']) == 0:
#                print "CREATE USER 1.0 - NEW USER!"
                cursorres.execute('INSERT INTO users (id, coursekeyword, name, email, username, password) VALUES (NULL,?,?,?,?,?)', [request.form['coursekeyword'],request.form['name'],request.form['email'],request.form['username'],request.form['password']])
                connres.commit()
                USER_SESSION["USER"] = request.form['username']
                return render_template('index.html',userlogged="Dear " + request.form['username'] +" your user has been created sucessfully. Now please click LOG IN above to have access to the entire web site content.")
            else:
                return render_template('index.html',userlogged="USER NOT CREATED! Sorry, the username = '" + request.form['username'] +"' is already in use, please choose a different one.")

        except:
            return render_template('index.html',userlogged="AN ERROR HAS OCURRED, USER HAS NOT BEEN CREATED! Please try again!")
    else:
        return render_template('index.html',userlogged="USER NOT CREATED! Sorry, you have included the wrong COURSEKEYWORD, please try again using the correct one.")



###############################################################
#         EVERY REQUEST BELOW NEEDS PASSWORD - START          #
###############################################################
from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_pw(username, password):
    global USER_SESSION, connres
    USER_SESSION["USER"]= username
    USER_SESSION["PWD"] = password
    try:
        realpassword = str(sql.read_sql("select password from users WHERE username = '"+str(username)+"'", connres)["password"][0])
#        print "realpassword=",realpassword
        USER_SESSION["PWD_VALID"] = realpassword
        if password == realpassword:
                return realpassword
    except:
#        print "users does not exist!"
        return None

@app.route('/login')
@auth.login_required
def login():
#    userdata = sql.read_sql('select * from users', connres)
#    print userdata
    return render_template('index.html',userlogged="Welcome " + USER_SESSION["USER"] + ", you are now logged in.")


@app.route('/userslogged', methods=['GET','POST'])
@auth.login_required
def userslogged():
    userdata = sql.read_sql('select * from users', connres)
    return userdata.to_json()

###############################################################
#         EVERY REQUEST ABOVE NEEDS PASSWORD - END            #
###############################################################

#@app.route('/predict0/<uuid>', methods=['GET','POST'])
#def predict0(uuid):
#    content = request.json
#    print content['BB_1YR_DEFAULT_PROB_CQ4_2013']
#    return jsonify({"uuid":content['BB_1YR_DEFAULT_PROB_CQ4_2013']})



print "IMPORTING LIBRARIES..."
import pandas as pd
import numpy as np
import requests
import pickle
import cPickle


#DOWLOADING FILE FROM DROPBOX FIRST TIME
import os.path
import time
import random
while not os.path.exists('EX2_DATA_BASE.xlsx'):
    time.sleep (3*random.random()); #Sleeping less than 3 seconds before going to Dropbox - avoid too many students at once.
    if not os.path.exists('EX2_DATA_BASE.xlsx'):
        print "DOWLOADING FILE EX2_DATA_BASE.xlsx FROM DROPBOX BECAUSE LOCAL FILE DOES NOT EXIST!"
#        csvfile = urllib2.urlopen("https://dl.dropboxusercontent.com/u/28535341/EX2_DEV_DATA.xlsx")
        resp = requests.get("https://dl.dropboxusercontent.com/u/28535341/EX2_DATA_BASE.xlsx")
        output = open('EX2_DATA_BASE.xlsx','wb')
        output.write(resp.content)
        output.close()
#DOWLOADING FILE FROM DROPBOX FIRST TIME


print "LOADING DATASETS..."
#df = pd.read_csv("EX2_DEV_DATA.xlsx",sep=";") #DEV-SAMPLE
df = pd.read_excel(open('EX2_DATA_BASE.xlsx','rb'), sheetname='DATA')
df_dictionary = pd.read_excel(open('EX2_DATA_BASE.xlsx','rb'), sheetname='DICTIONARY')

print "GETTING LIST OF VARIABLES..."
print "-> targe variable:"
target_variable = str(df_dictionary[df_dictionary['TYPE_OF_VARIABLE'] == 'TARGET']['FIELD_NAME'].tolist()[0])
print "target_variable = ",target_variable

# Quitamos las variables que no son continuas y no aportan información
list_of_inputs_for_model0 = df_dictionary[df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT0']['FIELD_NAME'].tolist()
list_of_inputs_for_model0.remove('TICKER')
list_of_inputs_for_model0.remove('NAME')
list_of_inputs_for_model0.remove('INDUSTRY_GROUP')
print "list_of_inputs_for_model0 = ",list_of_inputs_for_model0

list_of_inputs_for_model1 = df_dictionary[(df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT0') | (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT1')]['FIELD_NAME'].tolist()
list_of_inputs_for_model1.remove('TICKER')
list_of_inputs_for_model1.remove('NAME')
list_of_inputs_for_model1.remove('INDUSTRY_GROUP')
print "list_of_inputs_for_model1 = ",list_of_inputs_for_model1

list_of_inputs_for_model2 = df_dictionary[(df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT0') | (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT1')| (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT2')]['FIELD_NAME'].tolist()
list_of_inputs_for_model2.remove('TICKER')
list_of_inputs_for_model2.remove('NAME')
list_of_inputs_for_model2.remove('INDUSTRY_GROUP')
print "list_of_inputs_for_model2 = ",list_of_inputs_for_model2

list_of_inputs_for_model3 = df_dictionary[(df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT0') | (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT1')| (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT2')| (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT3')]['FIELD_NAME'].tolist()
list_of_inputs_for_model3.remove('TICKER')
list_of_inputs_for_model3.remove('NAME')
list_of_inputs_for_model3.remove('INDUSTRY_GROUP')
print "list_of_inputs_for_model3 = ",list_of_inputs_for_model3

list_of_inputs_for_model4 = df_dictionary[(df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT0') | (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT1')| (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT2')| (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT3')| (df_dictionary['TYPE_OF_VARIABLE'] == 'INPUT4')]['FIELD_NAME'].tolist()
list_of_inputs_for_model4.remove('TICKER')
list_of_inputs_for_model4.remove('NAME')
list_of_inputs_for_model4.remove('INDUSTRY_GROUP')
print "list_of_inputs_for_model4 = ",list_of_inputs_for_model4


@app.route('/api/predict0/<uuid>', methods=['GET', 'POST'])
def predict0(uuid):
    if uuid != '1234':
        return jsonify({"error":"user not unauthorised, wrong API key."})
    content = request.json
    df = pd.read_json(content, typ='series', orient='split')
    df = pd.read_json(content, typ='series', orient='split')

    # Creación de ratios
    # Return on Equity
    df['ROE_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001) # Para que no divida entre 0
    df['ROE_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    # Return on Assets
    df['ROA_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROA_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']++0.000000000001)
    # Enterprise Value / EBITDA
    df['EV_EBITDA_CQ4_2013'] = (df['CUR_MKT_CAP_CQ4_2013']+df['BS_CUR_LIAB_CQ4_2013']+df['NON_CUR_LIAB_CQ4_2013']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2013'])/(df['IS_EBITDA_CQ4_2013']+0.000000000001)
    df['EV_EBITDA_CQ4_2014'] = (df['CUR_MKT_CAP_CQ4_2014']+df['BS_CUR_LIAB_CQ4_2014']+df['NON_CUR_LIAB_CQ4_2014']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2014'])/(df['IS_EBITDA_CQ4_2014']++0.000000000001)
    # Fondo de maniobra
    df['FONDO_MANIOBRA_CQ4_2013'] = df['BS_CUR_ASSET_REPORT_CQ4_2013'] - df['BS_CUR_LIAB_CQ4_2013']
    df['FONDO_MANIOBRA_CQ4_2014'] = df['BS_CUR_ASSET_REPORT_CQ4_2014'] - df['BS_CUR_LIAB_CQ4_2014']
    # Ratio de endeudamiento a corto plazo
    df['DEUDA_CUR_CQ4_2013'] = df['BS_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_CUR_CQ4_2014'] = df['BS_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    # Ratio de endeudamiento a largo plazo
    df['DEUDA_NON_CUR_CQ4_2013'] = df['NON_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_NON_CUR_CQ4_2014'] = df['NON_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    # Rotación de activos
    df['ROTACION_ACTIVOS_CQ4_2013'] = df['SALES_REV_TURN_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ4_2014'] = df['SALES_REV_TURN_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    # Margen operativo
    df['MARGEN_OPERATIVO_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    # Productividad del personal
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['IS_PERSONNEL_EXP_CQ4_2013']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['IS_PERSONNEL_EXP_CQ4_2014']+0.000000000001)

    # Eliminamos valores NaN y Inf
    df = df.replace(-np.inf, 0)
    df = df.replace(np.inf, 0)
    df = df.fillna(0)

    # La selección de variables se ha hecho en el modelo de entrenamiento, utilizando la función mutual_info_regression del paquete scikit-learn.
    # Se ha establecido un filtro de una MI mínima de 0.1

    in_model0 = [u'IS_DEPRECIATION_AND_AMORTIZATION_FY_2014', u'NET_INCOME_CQ4_2014', u'BEST_TARGET_PRICE_FY_2013', u'BEST_TARGET_PRICE_FY_2014', u'BEST_TARGET_PRICE_CQ4_2013', u'BEST_TARGET_PRICE_CQ1_2014',
    u'BEST_TARGET_PRICE_CQ4_2014', u'BEST_TARGET_HI_FY_2014', u'BEST_TARGET_HI_CQ1_2014', u'BEST_TARGET_HI_CQ3_2014', u'BEST_TARGET_HI_CQ4_2014', u'BEST_TARGET_LO_FY_2013', u'BEST_TARGET_LO_FY_2014', u'BEST_TARGET_LO_CQ1_2014',
    u'BEST_TARGET_LO_CQ4_2014', u'BEST_TARGET_MEDIAN_FY_2013', u'BEST_TARGET_MEDIAN_FY_2014', u'BEST_TARGET_MEDIAN_CQ4_2013', u'BEST_TARGET_MEDIAN_CQ1_2014', u'BEST_TARGET_MEDIAN_CQ4_2014', u'CUR_MKT_CAP_CQ4_2014',
    u'BB_1YR_DEFAULT_PROB_CQ4_2013', u'BB_1YR_DEFAULT_PROB_CQ1_2014', u'BB_1YR_DEFAULT_PROB_CQ2_2014', u'BB_1YR_DEFAULT_PROB_CQ3_2014', u'BB_1YR_DEFAULT_PROB_CQ4_2014', 'FONDO_MANIOBRA_CQ4_2014', 'DEUDA_CUR_CQ4_2013',
    'DEUDA_CUR_CQ4_2014', 'DEUDA_NON_CUR_CQ4_2014', 'MARGEN_OPERATIVO_CQ4_2014']

    X = df[in_model0]

    with open('/home/EJCIFF2017/models/model0.pkl', 'rb') as f:
        model0 = cPickle.load(f)

#    d = json.loads(content)
#    print df.columns
    for item in list_of_inputs_for_model0:
        print item," = ", df[item]

    #IMPLEMENT HERE MY MODEL 0
    myprediction0 = str(model0.predict(X)[0])
    return jsonify({"prediction":myprediction0})


@app.route('/api/predict1/<uuid>', methods=['GET', 'POST'])
def predict1(uuid):
    if uuid != '1234':
        return jsonify({"error":"user not unauthorised, wrong API key."})
    content = request.json
    df = pd.read_json(content, typ='series', orient='split')
    df = pd.read_json(content, typ='series', orient='split')
    df = df.fillna(0)

    # Creación de ratios
    # Return on Equity
    df['ROE_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['ROE_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['ROE_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    # Return on Assets
    df['ROA_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROA_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROA_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    # Enterprise Value / EBITDA
    df['EV_EBITDA_CQ4_2013'] = (df['CUR_MKT_CAP_CQ4_2013']+df['BS_CUR_LIAB_CQ4_2013']+df['NON_CUR_LIAB_CQ4_2013']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2013'])/(df['IS_EBITDA_CQ4_2013']+0.000000000001)
    df['EV_EBITDA_CQ4_2014'] = (df['CUR_MKT_CAP_CQ4_2014']+df['BS_CUR_LIAB_CQ4_2014']+df['NON_CUR_LIAB_CQ4_2014']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2014'])/(df['IS_EBITDA_CQ4_2014']+0.000000000001)
    df['EV_EBITDA_CQ1_2015'] = (df['CUR_MKT_CAP_CQ1_2015']+df['BS_CUR_LIAB_CQ1_2015']+df['NON_CUR_LIAB_CQ1_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ1_2015'])/(df['IS_EBITDA_CQ1_2015']+0.000000000001)
    # Fondo de maniobra
    df['FONDO_MANIOBRA_CQ4_2013'] = df['BS_CUR_ASSET_REPORT_CQ4_2013'] - df['BS_CUR_LIAB_CQ4_2013']
    df['FONDO_MANIOBRA_CQ4_2014'] = df['BS_CUR_ASSET_REPORT_CQ4_2014'] - df['BS_CUR_LIAB_CQ4_2014']
    df['FONDO_MANIOBRA_CQ1_2015'] = df['BS_CUR_ASSET_REPORT_CQ1_2015'] - df['BS_CUR_LIAB_CQ1_2015']
    # Ratio de endeudamiento a corto plazo
    df['DEUDA_CUR_CQ4_2013'] = df['BS_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_CUR_CQ4_2014'] = df['BS_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_CUR_CQ1_2015'] = df['BS_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    # Ratio de endeudamiento a largo plazo
    df['DEUDA_NON_CUR_CQ4_2013'] = df['NON_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_NON_CUR_CQ4_2014'] = df['NON_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_NON_CUR_CQ1_2015'] = df['NON_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    # Rotación de activos
    df['ROTACION_ACTIVOS_CQ4_2013'] = df['SALES_REV_TURN_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ4_2014'] = df['SALES_REV_TURN_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ1_2015'] = df['SALES_REV_TURN_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    # Margen operativo
    df['MARGEN_OPERATIVO_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    # Productividad del personal
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['IS_PERSONNEL_EXP_CQ4_2013']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['IS_PERSONNEL_EXP_CQ4_2014']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['IS_PERSONNEL_EXP_CQ1_2015']+0.000000000001)

    # Eliminamos valores NaN y Inf
    df = df.replace(-np.inf, 0)
    df = df.replace(np.inf, 0)
    df = df.fillna(0)

    # La selección de variables se ha hecho en el modelo de entrenamiento, utilizando la función mutual_info_regression del paquete scikit-learn.
    # Se ha establecido un filtro de una MI mínima de 0.1

    in_model1 = [u'IS_DEPRECIATION_AND_AMORTIZATION_FY_2014', u'NET_INCOME_CQ4_2014', u'NET_INCOME_CQ1_2015', u'BEST_TARGET_PRICE_FY_2013', u'BEST_TARGET_PRICE_FY_2014', u'BEST_TARGET_PRICE_CQ4_2013', u'BEST_TARGET_PRICE_CQ4_2014',
    u'BEST_TARGET_HI_FY_2013', u'BEST_TARGET_HI_FY_2014', u'BEST_TARGET_HI_CQ1_2014', u'BEST_TARGET_HI_CQ4_2014', u'BEST_TARGET_LO_FY_2013', u'BEST_TARGET_LO_FY_2014', u'BEST_TARGET_LO_CQ1_2014', u'BEST_TARGET_LO_CQ4_2014',
    u'BEST_TARGET_LO_CQ1_2015', u'BEST_TARGET_MEDIAN_FY_2013', u'BEST_TARGET_MEDIAN_FY_2014', u'BEST_TARGET_MEDIAN_CQ4_2013', u'BEST_TARGET_MEDIAN_CQ1_2014', u'BEST_TARGET_MEDIAN_CQ3_2014', u'BEST_TARGET_MEDIAN_CQ4_2014',
    u'CUR_MKT_CAP_CQ4_2014', u'CUR_MKT_CAP_CQ1_2015', u'BB_1YR_DEFAULT_PROB_CQ4_2013', u'BB_1YR_DEFAULT_PROB_CQ1_2014', u'BB_1YR_DEFAULT_PROB_CQ2_2014', u'BB_1YR_DEFAULT_PROB_CQ3_2014', u'BB_1YR_DEFAULT_PROB_CQ4_2014',
    u'BB_1YR_DEFAULT_PROB_CQ1_2015', 'ROE_CQ4_2014', 'ROE_CQ1_2015', 'FONDO_MANIOBRA_CQ4_2014', 'DEUDA_CUR_CQ4_2013', 'DEUDA_CUR_CQ4_2014','DEUDA_NON_CUR_CQ4_2014', 'MARGEN_OPERATIVO_CQ4_2014', 'PRODUCTIVIDAD_PERSONAL_CQ1_2015']

    X = df[in_model1]

    with open('/home/EJCIFF2017/models/model1.pkl', 'rb') as f:
        model1 = cPickle.load(f)

#    d = json.loads(content)
#    print df.columns
    for item in list_of_inputs_for_model1:
        print item," = ", df[item]

    myprediction1 = str(model1.predict(X)[0])
    return jsonify({"prediction":myprediction1})

@app.route('/api/predict2/<uuid>', methods=['GET', 'POST'])
def predict2(uuid):
    if uuid != '1234':
        return jsonify({"error":"user not unauthorised, wrong API key."})
    content = request.json
    df = pd.read_json(content, typ='series', orient='split')
    df = pd.read_json(content, typ='series', orient='split')
    df = df.fillna(0)

    # Creación de ratios
    # Return on Equity
    df['ROE_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['ROE_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['ROE_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['ROE_CQ2_2015'] = df['NET_INCOME_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    # Return on Assets
    df['ROA_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROA_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROA_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['ROA_CQ2_2015'] = df['NET_INCOME_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    # Enterprise Value / EBITDA
    df['EV_EBITDA_CQ4_2013'] = (df['CUR_MKT_CAP_CQ4_2013']+df['BS_CUR_LIAB_CQ4_2013']+df['NON_CUR_LIAB_CQ4_2013']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2013'])/(df['IS_EBITDA_CQ4_2013']+0.000000000001)
    df['EV_EBITDA_CQ4_2014'] = (df['CUR_MKT_CAP_CQ4_2014']+df['BS_CUR_LIAB_CQ4_2014']+df['NON_CUR_LIAB_CQ4_2014']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2014'])/(df['IS_EBITDA_CQ4_2014']+0.000000000001)
    df['EV_EBITDA_CQ1_2015'] = (df['CUR_MKT_CAP_CQ1_2015']+df['BS_CUR_LIAB_CQ1_2015']+df['NON_CUR_LIAB_CQ1_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ1_2015'])/(df['IS_EBITDA_CQ1_2015']+0.000000000001)
    df['EV_EBITDA_CQ2_2015'] = (df['CUR_MKT_CAP_CQ2_2015']+df['BS_CUR_LIAB_CQ2_2015']+df['NON_CUR_LIAB_CQ2_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ2_2015'])/(df['IS_EBITDA_CQ2_2015']+0.000000000001)
    # Fondo de maniobra
    df['FONDO_MANIOBRA_CQ4_2013'] = df['BS_CUR_ASSET_REPORT_CQ4_2013'] - df['BS_CUR_LIAB_CQ4_2013']
    df['FONDO_MANIOBRA_CQ4_2014'] = df['BS_CUR_ASSET_REPORT_CQ4_2014'] - df['BS_CUR_LIAB_CQ4_2014']
    df['FONDO_MANIOBRA_CQ1_2015'] = df['BS_CUR_ASSET_REPORT_CQ1_2015'] - df['BS_CUR_LIAB_CQ1_2015']
    df['FONDO_MANIOBRA_CQ2_2015'] = df['BS_CUR_ASSET_REPORT_CQ2_2015'] - df['BS_CUR_LIAB_CQ2_2015']
    # Ratio de endeudamiento a corto plazo
    df['DEUDA_CUR_CQ4_2013'] = df['BS_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_CUR_CQ4_2014'] = df['BS_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_CUR_CQ1_2015'] = df['BS_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['DEUDA_CUR_CQ2_2015'] = df['BS_CUR_LIAB_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    # Ratio de endeudamiento a largo plazo
    df['DEUDA_NON_CUR_CQ4_2013'] = df['NON_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_NON_CUR_CQ4_2014'] = df['NON_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_NON_CUR_CQ1_2015'] = df['NON_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['DEUDA_NON_CUR_CQ2_2015'] = df['NON_CUR_LIAB_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    # Rotación de activos
    df['ROTACION_ACTIVOS_CQ4_2013'] = df['SALES_REV_TURN_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ4_2014'] = df['SALES_REV_TURN_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ1_2015'] = df['SALES_REV_TURN_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ2_2015'] = df['SALES_REV_TURN_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    # Margen operativo
    df['MARGEN_OPERATIVO_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ2_2015'] = df['IS_OPER_INC_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    # Productividad del personal
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['IS_PERSONNEL_EXP_CQ4_2013']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['IS_PERSONNEL_EXP_CQ4_2014']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['IS_PERSONNEL_EXP_CQ1_2015']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ2_2015'] = df['IS_OPER_INC_CQ2_2015']/(df['IS_PERSONNEL_EXP_CQ2_2015']+0.000000000001)

    # Eliminamos valores NaN y Inf
    df = df.replace(-np.inf, 0)
    df = df.replace(np.inf, 0)
    df = df.fillna(0)

    # La selección de variables se ha hecho en el modelo de entrenamiento, utilizando la función mutual_info_regression del paquete scikit-learn.
    # Se ha establecido un filtro de una MI mínima de 0.1

    in_model2 = [u'IS_DEPRECIATION_AND_AMORTIZATION_FY_2014', u'IS_OPER_INC_CQ2_2015', u'PRETAX_INC_CQ2_2015', u'IS_INC_TAX_EXP_CQ2_2015', u'NET_INCOME_CQ4_2014', u'BEST_TARGET_PRICE_FY_2013', u'BEST_TARGET_PRICE_FY_2014',
    u'BEST_TARGET_PRICE_CQ4_2013', u'BEST_TARGET_PRICE_CQ1_2014', u'BEST_TARGET_PRICE_CQ4_2014', u'BEST_TARGET_PRICE_CQ2_2015', u'BEST_TARGET_HI_FY_2014', u'BEST_TARGET_HI_CQ4_2014', u'BEST_TARGET_HI_CQ2_2015',
    u'BEST_TARGET_LO_FY_2014', u'BEST_TARGET_LO_CQ4_2013', u'BEST_TARGET_LO_CQ1_2014', u'BEST_TARGET_LO_CQ4_2014', u'BEST_TARGET_LO_CQ1_2015', u'BEST_TARGET_LO_CQ2_2015', u'BEST_TARGET_MEDIAN_FY_2013', u'BEST_TARGET_MEDIAN_FY_2014',
    u'BEST_TARGET_MEDIAN_CQ4_2013', u'BEST_TARGET_MEDIAN_CQ1_2014', u'BEST_TARGET_MEDIAN_CQ4_2014', u'BEST_TARGET_MEDIAN_CQ2_2015', u'CUR_MKT_CAP_CQ4_2014', u'CUR_MKT_CAP_CQ1_2015', u'CUR_MKT_CAP_CQ2_2015',
    u'BB_1YR_DEFAULT_PROB_CQ4_2013', u'BB_1YR_DEFAULT_PROB_CQ1_2014', u'BB_1YR_DEFAULT_PROB_CQ2_2014', u'BB_1YR_DEFAULT_PROB_CQ3_2014', u'BB_1YR_DEFAULT_PROB_CQ4_2014', u'BB_1YR_DEFAULT_PROB_CQ1_2015',
    u'BB_1YR_DEFAULT_PROB_CQ2_2015', 'ROE_CQ4_2014', 'ROE_CQ1_2015', 'ROA_CQ2_2015', 'FONDO_MANIOBRA_CQ4_2014', 'DEUDA_CUR_CQ4_2013', 'DEUDA_CUR_CQ4_2014', 'DEUDA_CUR_CQ1_2015', 'DEUDA_NON_CUR_CQ4_2014', 'DEUDA_NON_CUR_CQ2_2015',
    'MARGEN_OPERATIVO_CQ4_2014', 'MARGEN_OPERATIVO_CQ2_2015', 'PRODUCTIVIDAD_PERSONAL_CQ1_2015']

    X = df[in_model2]

    with open('/home/EJCIFF2017/models/model2.pkl', 'rb') as f:
        model2 = cPickle.load(f)


#    d = json.loads(content)
#    print df.columns
    for item in list_of_inputs_for_model2:
        print item," = ", df[item]

    myprediction2 = str(model2.predict(X)[0])
    return jsonify({"prediction":myprediction2})


@app.route('/api/predict3/<uuid>', methods=['GET', 'POST'])
def predict3(uuid):
    if uuid != '1234':
        return jsonify({"error":"user not unauthorised, wrong API key."})
    content = request.json
    df = pd.read_json(content, typ='series', orient='split')
    df = pd.read_json(content, typ='series', orient='split')
    df = df.fillna(0)

    # Creación de ratios
    # Return on Equity
    df['ROE_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['ROE_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['ROE_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['ROE_CQ2_2015'] = df['NET_INCOME_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    df['ROE_CQ3_2015'] = df['NET_INCOME_CQ3_2015']/(df['TOTAL_EQUITY_CQ3_2015']+0.000000000001)
    # Return on Assets
    df['ROA_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROA_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROA_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['ROA_CQ2_2015'] = df['NET_INCOME_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    df['ROA_CQ3_2015'] = df['NET_INCOME_CQ3_2015']/(df['BS_TOT_ASSET_CQ3_2015']+0.000000000001)
    # Enterprise Value / EBITDA
    df['EV_EBITDA_CQ4_2013'] = (df['CUR_MKT_CAP_CQ4_2013']+df['BS_CUR_LIAB_CQ4_2013']+df['NON_CUR_LIAB_CQ4_2013']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2013'])/(df['IS_EBITDA_CQ4_2013']+0.000000000001)
    df['EV_EBITDA_CQ4_2014'] = (df['CUR_MKT_CAP_CQ4_2014']+df['BS_CUR_LIAB_CQ4_2014']+df['NON_CUR_LIAB_CQ4_2014']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2014'])/(df['IS_EBITDA_CQ4_2014']+0.000000000001)
    df['EV_EBITDA_CQ1_2015'] = (df['CUR_MKT_CAP_CQ1_2015']+df['BS_CUR_LIAB_CQ1_2015']+df['NON_CUR_LIAB_CQ1_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ1_2015'])/(df['IS_EBITDA_CQ1_2015']+0.000000000001)
    df['EV_EBITDA_CQ2_2015'] = (df['CUR_MKT_CAP_CQ2_2015']+df['BS_CUR_LIAB_CQ2_2015']+df['NON_CUR_LIAB_CQ2_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ2_2015'])/(df['IS_EBITDA_CQ2_2015']+0.000000000001)
    df['EV_EBITDA_CQ3_2015'] = (df['CUR_MKT_CAP_CQ3_2015']+df['BS_CUR_LIAB_CQ3_2015']+df['NON_CUR_LIAB_CQ3_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ3_2015'])/(df['IS_EBITDA_CQ3_2015']+0.000000000001)
    # Fondo de maniobra
    df['FONDO_MANIOBRA_CQ4_2013'] = df['BS_CUR_ASSET_REPORT_CQ4_2013'] - df['BS_CUR_LIAB_CQ4_2013']
    df['FONDO_MANIOBRA_CQ4_2014'] = df['BS_CUR_ASSET_REPORT_CQ4_2014'] - df['BS_CUR_LIAB_CQ4_2014']
    df['FONDO_MANIOBRA_CQ1_2015'] = df['BS_CUR_ASSET_REPORT_CQ1_2015'] - df['BS_CUR_LIAB_CQ1_2015']
    df['FONDO_MANIOBRA_CQ2_2015'] = df['BS_CUR_ASSET_REPORT_CQ2_2015'] - df['BS_CUR_LIAB_CQ2_2015']
    df['FONDO_MANIOBRA_CQ3_2015'] = df['BS_CUR_ASSET_REPORT_CQ3_2015'] - df['BS_CUR_LIAB_CQ3_2015']
    # Ratio de endeudamiento a corto plazo
    df['DEUDA_CUR_CQ4_2013'] = df['BS_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_CUR_CQ4_2014'] = df['BS_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_CUR_CQ1_2015'] = df['BS_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['DEUDA_CUR_CQ2_2015'] = df['BS_CUR_LIAB_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    df['DEUDA_CUR_CQ3_2015'] = df['BS_CUR_LIAB_CQ3_2015']/(df['TOTAL_EQUITY_CQ3_2015']+0.000000000001)
    # Ratio de endeudamiento a largo plazo
    df['DEUDA_NON_CUR_CQ4_2013'] = df['NON_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_NON_CUR_CQ4_2014'] = df['NON_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_NON_CUR_CQ1_2015'] = df['NON_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['DEUDA_NON_CUR_CQ2_2015'] = df['NON_CUR_LIAB_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    df['DEUDA_NON_CUR_CQ3_2015'] = df['NON_CUR_LIAB_CQ3_2015']/(df['TOTAL_EQUITY_CQ3_2015']+0.000000000001)
    # Rotación de activos
    df['ROTACION_ACTIVOS_CQ4_2013'] = df['SALES_REV_TURN_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ4_2014'] = df['SALES_REV_TURN_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ1_2015'] = df['SALES_REV_TURN_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ2_2015'] = df['SALES_REV_TURN_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ3_2015'] = df['SALES_REV_TURN_CQ3_2015']/(df['BS_TOT_ASSET_CQ3_2015']+0.000000000001)
    # Margen operativo
    df['MARGEN_OPERATIVO_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ2_2015'] = df['IS_OPER_INC_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ3_2015'] = df['IS_OPER_INC_CQ3_2015']/(df['BS_TOT_ASSET_CQ3_2015']+0.000000000001)
    # Productividad del personal
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['IS_PERSONNEL_EXP_CQ4_2013']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['IS_PERSONNEL_EXP_CQ4_2014']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['IS_PERSONNEL_EXP_CQ1_2015']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ2_2015'] = df['IS_OPER_INC_CQ2_2015']/(df['IS_PERSONNEL_EXP_CQ2_2015']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ3_2015'] = df['IS_OPER_INC_CQ3_2015']/(df['IS_PERSONNEL_EXP_CQ3_2015']+0.000000000001)

    # Eliminamos valores NaN y Inf
    df = df.replace(-np.inf, 0)
    df = df.replace(np.inf, 0)
    df = df.fillna(0)

    # La selección de variables se ha hecho en el modelo de entrenamiento, utilizando la función mutual_info_regression del paquete scikit-learn.
    # Se ha establecido un filtro de una MI mínima de 0.1

    in_model3 = [u'IS_DEPRECIATION_AND_AMORTIZATION_FY_2014', u'IS_OPER_INC_CQ2_2015', u'PRETAX_INC_CQ2_2015', u'IS_INC_TAX_EXP_CQ2_2015', u'NET_INCOME_CQ4_2014', u'BEST_TARGET_PRICE_FY_2013', u'BEST_TARGET_PRICE_FY_2014',
    u'BEST_TARGET_PRICE_CQ4_2013', u'BEST_TARGET_PRICE_CQ1_2014', u'BEST_TARGET_PRICE_CQ4_2014', u'BEST_TARGET_PRICE_CQ2_2015', u'BEST_TARGET_PRICE_CQ3_2015', u'BEST_TARGET_HI_FY_2014', u'BEST_TARGET_HI_CQ1_2014',
    u'BEST_TARGET_HI_CQ4_2014', u'BEST_TARGET_HI_CQ2_2015', u'BEST_TARGET_HI_CQ3_2015', u'BEST_TARGET_LO_FY_2014', u'BEST_TARGET_LO_CQ1_2014', u'BEST_TARGET_LO_CQ4_2014', u'BEST_TARGET_LO_CQ1_2015', u'BEST_TARGET_LO_CQ2_2015',
    u'BEST_TARGET_LO_CQ3_2015', u'BEST_TARGET_MEDIAN_FY_2013', u'BEST_TARGET_MEDIAN_CQ4_2013', u'BEST_TARGET_MEDIAN_CQ1_2014', u'BEST_TARGET_MEDIAN_CQ2_2015', u'BEST_TARGET_MEDIAN_CQ3_2015', u'CUR_MKT_CAP_CQ4_2014',
    u'CUR_MKT_CAP_CQ1_2015', u'CUR_MKT_CAP_CQ2_2015', u'CUR_MKT_CAP_CQ3_2015', u'BB_1YR_DEFAULT_PROB_CQ4_2013', u'BB_1YR_DEFAULT_PROB_CQ1_2014', u'BB_1YR_DEFAULT_PROB_CQ2_2014', u'BB_1YR_DEFAULT_PROB_CQ3_2014',
    u'BB_1YR_DEFAULT_PROB_CQ4_2014', u'BB_1YR_DEFAULT_PROB_CQ1_2015', u'BB_1YR_DEFAULT_PROB_CQ2_2015', u'BB_1YR_DEFAULT_PROB_CQ3_2015', 'ROE_CQ4_2014', 'ROE_CQ1_2015', 'ROE_CQ2_2015', 'ROA_CQ2_2015', 'ROA_CQ3_2015',
    'FONDO_MANIOBRA_CQ4_2014', 'DEUDA_CUR_CQ4_2013', 'DEUDA_CUR_CQ4_2014', 'DEUDA_NON_CUR_CQ4_2014', 'DEUDA_NON_CUR_CQ2_2015', 'MARGEN_OPERATIVO_CQ4_2014', 'MARGEN_OPERATIVO_CQ2_2015', 'PRODUCTIVIDAD_PERSONAL_CQ1_2015']

    X = df[in_model3]

    with open('/home/EJCIFF2017/models/model3.pkl', 'rb') as f:
        model3 = cPickle.load(f)


#    d = json.loads(content)
#    print df.columns
    for item in list_of_inputs_for_model3:
        print item," = ", df[item]

    myprediction3 = str(model3.predict(X)[0])
    return jsonify({"prediction":myprediction3})

@app.route('/api/predict4/<uuid>', methods=['GET', 'POST'])
def predict4(uuid):
    if uuid != '1234':
        return jsonify({"error":"user not unauthorised, wrong API key."})
    content = request.json
    df = pd.read_json(content, typ='series', orient='split')
    df = pd.read_json(content, typ='series', orient='split')
    df = df.fillna(0)

    # Creación de ratios
    # Return on Equity
    df['ROE_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['ROE_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['ROE_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['ROE_CQ2_2015'] = df['NET_INCOME_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    df['ROE_CQ3_2015'] = df['NET_INCOME_CQ3_2015']/(df['TOTAL_EQUITY_CQ3_2015']+0.000000000001)
    df['ROE_CQ4_2015'] = df['NET_INCOME_CQ4_2015']/(df['TOTAL_EQUITY_CQ4_2015']+0.000000000001)
    # Return on Assets
    df['ROA_CQ4_2013'] = df['NET_INCOME_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROA_CQ4_2014'] = df['NET_INCOME_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROA_CQ1_2015'] = df['NET_INCOME_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['ROA_CQ2_2015'] = df['NET_INCOME_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    df['ROA_CQ3_2015'] = df['NET_INCOME_CQ3_2015']/(df['BS_TOT_ASSET_CQ3_2015']+0.000000000001)
    df['ROA_CQ4_2015'] = df['NET_INCOME_CQ4_2015']/(df['BS_TOT_ASSET_CQ4_2015']+0.000000000001)
    # Enterprise Value / EBITDA
    df['EV_EBITDA_CQ4_2013'] = (df['CUR_MKT_CAP_CQ4_2013']+df['BS_CUR_LIAB_CQ4_2013']+df['NON_CUR_LIAB_CQ4_2013']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2013'])/(df['IS_EBITDA_CQ4_2013']+0.000000000001)
    df['EV_EBITDA_CQ4_2014'] = (df['CUR_MKT_CAP_CQ4_2014']+df['BS_CUR_LIAB_CQ4_2014']+df['NON_CUR_LIAB_CQ4_2014']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2014'])/(df['IS_EBITDA_CQ4_2014']+0.000000000001)
    df['EV_EBITDA_CQ1_2015'] = (df['CUR_MKT_CAP_CQ1_2015']+df['BS_CUR_LIAB_CQ1_2015']+df['NON_CUR_LIAB_CQ1_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ1_2015'])/(df['IS_EBITDA_CQ1_2015']+0.000000000001)
    df['EV_EBITDA_CQ2_2015'] = (df['CUR_MKT_CAP_CQ2_2015']+df['BS_CUR_LIAB_CQ2_2015']+df['NON_CUR_LIAB_CQ2_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ2_2015'])/(df['IS_EBITDA_CQ2_2015']+0.000000000001)
    df['EV_EBITDA_CQ3_2015'] = (df['CUR_MKT_CAP_CQ3_2015']+df['BS_CUR_LIAB_CQ3_2015']+df['NON_CUR_LIAB_CQ3_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ3_2015'])/(df['IS_EBITDA_CQ3_2015']+0.000000000001)
    df['EV_EBITDA_CQ4_2015'] = (df['CUR_MKT_CAP_CQ4_2015']+df['BS_CUR_LIAB_CQ4_2015']+df['NON_CUR_LIAB_CQ4_2015']-df['BS_CASH_NEAR_CASH_ITEM_CQ4_2015'])/(df['IS_EBITDA_CQ4_2015']+0.000000000001)
    # Fondo de maniobra
    df['FONDO_MANIOBRA_CQ4_2013'] = df['BS_CUR_ASSET_REPORT_CQ4_2013'] - df['BS_CUR_LIAB_CQ4_2013']
    df['FONDO_MANIOBRA_CQ4_2014'] = df['BS_CUR_ASSET_REPORT_CQ4_2014'] - df['BS_CUR_LIAB_CQ4_2014']
    df['FONDO_MANIOBRA_CQ1_2015'] = df['BS_CUR_ASSET_REPORT_CQ1_2015'] - df['BS_CUR_LIAB_CQ1_2015']
    df['FONDO_MANIOBRA_CQ2_2015'] = df['BS_CUR_ASSET_REPORT_CQ2_2015'] - df['BS_CUR_LIAB_CQ2_2015']
    df['FONDO_MANIOBRA_CQ3_2015'] = df['BS_CUR_ASSET_REPORT_CQ3_2015'] - df['BS_CUR_LIAB_CQ3_2015']
    df['FONDO_MANIOBRA_CQ4_2015'] = df['BS_CUR_ASSET_REPORT_CQ4_2015'] - df['BS_CUR_LIAB_CQ4_2015']
    # Ratio de endeudamiento a corto plazo
    df['DEUDA_CUR_CQ4_2013'] = df['BS_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_CUR_CQ4_2014'] = df['BS_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_CUR_CQ1_2015'] = df['BS_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['DEUDA_CUR_CQ2_2015'] = df['BS_CUR_LIAB_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    df['DEUDA_CUR_CQ3_2015'] = df['BS_CUR_LIAB_CQ3_2015']/(df['TOTAL_EQUITY_CQ3_2015']+0.000000000001)
    df['DEUDA_CUR_CQ4_2015'] = df['BS_CUR_LIAB_CQ4_2015']/(df['TOTAL_EQUITY_CQ4_2015']+0.000000000001)
    # Ratio de endeudamiento a largo plazo
    df['DEUDA_NON_CUR_CQ4_2013'] = df['NON_CUR_LIAB_CQ4_2013']/(df['TOTAL_EQUITY_CQ4_2013']+0.000000000001)
    df['DEUDA_NON_CUR_CQ4_2014'] = df['NON_CUR_LIAB_CQ4_2014']/(df['TOTAL_EQUITY_CQ4_2014']+0.000000000001)
    df['DEUDA_NON_CUR_CQ1_2015'] = df['NON_CUR_LIAB_CQ1_2015']/(df['TOTAL_EQUITY_CQ1_2015']+0.000000000001)
    df['DEUDA_NON_CUR_CQ2_2015'] = df['NON_CUR_LIAB_CQ2_2015']/(df['TOTAL_EQUITY_CQ2_2015']+0.000000000001)
    df['DEUDA_NON_CUR_CQ3_2015'] = df['NON_CUR_LIAB_CQ3_2015']/(df['TOTAL_EQUITY_CQ3_2015']+0.000000000001)
    df['DEUDA_NON_CUR_CQ4_2015'] = df['NON_CUR_LIAB_CQ4_2015']/(df['TOTAL_EQUITY_CQ4_2015']+0.000000000001)
    # Rotación de activos
    df['ROTACION_ACTIVOS_CQ4_2013'] = df['SALES_REV_TURN_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ4_2014'] = df['SALES_REV_TURN_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ1_2015'] = df['SALES_REV_TURN_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ2_2015'] = df['SALES_REV_TURN_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ3_2015'] = df['SALES_REV_TURN_CQ3_2015']/(df['BS_TOT_ASSET_CQ3_2015']+0.000000000001)
    df['ROTACION_ACTIVOS_CQ4_2015'] = df['SALES_REV_TURN_CQ4_2015']/(df['BS_TOT_ASSET_CQ4_2015']+0.000000000001)
    # Margen operativo
    df['MARGEN_OPERATIVO_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['BS_TOT_ASSET_CQ4_2013']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['BS_TOT_ASSET_CQ4_2014']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['BS_TOT_ASSET_CQ1_2015']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ2_2015'] = df['IS_OPER_INC_CQ2_2015']/(df['BS_TOT_ASSET_CQ2_2015']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ3_2015'] = df['IS_OPER_INC_CQ3_2015']/(df['BS_TOT_ASSET_CQ3_2015']+0.000000000001)
    df['MARGEN_OPERATIVO_CQ4_2015'] = df['IS_OPER_INC_CQ4_2015']/(df['BS_TOT_ASSET_CQ4_2015']+0.000000000001)
    # Productividad del personal
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2013'] = df['IS_OPER_INC_CQ4_2013']/(df['IS_PERSONNEL_EXP_CQ4_2013']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2014'] = df['IS_OPER_INC_CQ4_2014']/(df['IS_PERSONNEL_EXP_CQ4_2014']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ1_2015'] = df['IS_OPER_INC_CQ1_2015']/(df['IS_PERSONNEL_EXP_CQ1_2015']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ2_2015'] = df['IS_OPER_INC_CQ2_2015']/(df['IS_PERSONNEL_EXP_CQ2_2015']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ3_2015'] = df['IS_OPER_INC_CQ3_2015']/(df['IS_PERSONNEL_EXP_CQ3_2015']+0.000000000001)
    df['PRODUCTIVIDAD_PERSONAL_CQ4_2015'] = df['IS_OPER_INC_CQ4_2015']/(df['IS_PERSONNEL_EXP_CQ4_2015']+0.000000000001)

    # Eliminamos valores NaN y Inf
    df = df.replace(-np.inf, 0)
    df = df.replace(np.inf, 0)
    df = df.fillna(0)

    # La selección de variables se ha hecho en el modelo de entrenamiento, utilizando la función mutual_info_regression del paquete scikit-learn.
    # Se ha establecido un filtro de una MI mínima de 0.1

    in_model4 = [u'SALES_REV_TURN_FY_2015', u'IS_COST_OF_MATL_FY_2015', u'IS_DEPRECIATION_AND_AMORTIZATION_FY_2014', u'IS_DEPRECIATION_AND_AMORTIZATION_FY_2015', u'IS_OPER_INC_CQ2_2015', u'PRETAX_INC_FY_2015',
    u'PRETAX_INC_CQ2_2015', u'PRETAX_INC_CQ4_2015', u'IS_INC_TAX_EXP_FY_2015', u'IS_INC_TAX_EXP_CQ2_2015', u'NET_INCOME_CQ4_2014', u'NET_INCOME_CQ1_2015', u'NET_INCOME_CQ4_2015', u'BEST_TARGET_PRICE_FY_2013',
    u'BEST_TARGET_PRICE_FY_2014', u'BEST_TARGET_PRICE_FY_2015', u'BEST_TARGET_PRICE_CQ4_2013', u'BEST_TARGET_PRICE_CQ1_2014', u'BEST_TARGET_PRICE_CQ4_2014', u'BEST_TARGET_PRICE_CQ2_2015', u'BEST_TARGET_PRICE_CQ3_2015',
    u'BEST_TARGET_PRICE_CQ4_2015', u'BEST_TARGET_HI_FY_2014', u'BEST_TARGET_HI_FY_2015', u'BEST_TARGET_HI_CQ1_2014', u'BEST_TARGET_HI_CQ4_2014', u'BEST_TARGET_HI_CQ2_2015', u'BEST_TARGET_HI_CQ3_2015', u'BEST_TARGET_HI_CQ4_2015',
    u'BEST_TARGET_LO_FY_2014', u'BEST_TARGET_LO_FY_2015', u'BEST_TARGET_LO_CQ4_2013', u'BEST_TARGET_LO_CQ1_2014', u'BEST_TARGET_LO_CQ4_2014', u'BEST_TARGET_LO_CQ1_2015', u'BEST_TARGET_LO_CQ2_2015', u'BEST_TARGET_LO_CQ3_2015',
    u'BEST_TARGET_LO_CQ4_2015', u'BEST_TARGET_MEDIAN_FY_2013', u'BEST_TARGET_MEDIAN_FY_2014', u'BEST_TARGET_MEDIAN_FY_2015', u'BEST_TARGET_MEDIAN_CQ4_2013', u'BEST_TARGET_MEDIAN_CQ1_2014', u'BEST_TARGET_MEDIAN_CQ4_2014',
    u'BEST_TARGET_MEDIAN_CQ2_2015', u'BEST_TARGET_MEDIAN_CQ3_2015', u'BEST_TARGET_MEDIAN_CQ4_2015', u'CUR_MKT_CAP_CQ4_2014', u'CUR_MKT_CAP_CQ1_2015', u'CUR_MKT_CAP_CQ2_2015', u'CUR_MKT_CAP_CQ3_2015', u'CUR_MKT_CAP_CQ4_2015',
    u'BB_1YR_DEFAULT_PROB_CQ4_2013', u'BB_1YR_DEFAULT_PROB_CQ1_2014', u'BB_1YR_DEFAULT_PROB_CQ2_2014', u'BB_1YR_DEFAULT_PROB_CQ3_2014', u'BB_1YR_DEFAULT_PROB_CQ4_2014', u'BB_1YR_DEFAULT_PROB_CQ1_2015', u'BB_1YR_DEFAULT_PROB_CQ2_2015',
    u'BB_1YR_DEFAULT_PROB_CQ3_2015', 'ROE_CQ4_2014', 'ROE_CQ1_2015', 'ROE_CQ2_2015', 'ROE_CQ4_2015', 'ROA_CQ2_2015', 'ROA_CQ3_2015', 'FONDO_MANIOBRA_CQ4_2014', 'DEUDA_CUR_CQ4_2013', 'DEUDA_CUR_CQ4_2014', 'DEUDA_CUR_CQ2_2015',
    'DEUDA_CUR_CQ4_2015', 'DEUDA_NON_CUR_CQ4_2014', 'DEUDA_NON_CUR_CQ2_2015', 'ROTACION_ACTIVOS_CQ4_2015', 'MARGEN_OPERATIVO_CQ4_2014', 'MARGEN_OPERATIVO_CQ2_2015', 'MARGEN_OPERATIVO_CQ4_2015', 'PRODUCTIVIDAD_PERSONAL_CQ1_2015']

    X = df[in_model4]

    with open('/home/EJCIFF2017/models/model4.pkl', 'rb') as f:
        model4 = cPickle.load(f)


#    d = json.loads(content)
#    print df.columns
    for item in list_of_inputs_for_model4:
        print item," = ", df[item]

    myprediction4 = str(model4.predict(X)[0])
    return jsonify({"prediction":myprediction4})

###############################################################################################################
#         INFINITY LOOP LISTENING TO PORT 80 (port=int("80")) FROM THE OUTSIDE WORLD (host="0.0.0.0") - START #
###############################################################################################################
if __name__ == '__main__':
    app.run(
	host="0.0.0.0",
        port=int("80")
#        ,	processes=9
#        debug=True
    )
###############################################################################################################
#         INFINITY LOOP LISTENING TO PORT 80 (port=int("80")) FROM THE OUTSIDE WORLD (host="0.0.0.0") - END   #
###############################################################################################################

