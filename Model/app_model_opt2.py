from flask import Flask, request, jsonify
import os
import pickle
# from sklearn.model_selection import cross_val_score
import pandas as pd

import sqlite3
from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error

os.chdir(os.path.dirname(__file__))
app = Flask(__name__)
app.config['DEBUG'] = True

# sqlite3 advert.db #on terminal

# def db_creation():
#     df=pd.read_csv('data/Advertising.csv')
#     connection = sqlite3.connect('data/Advertising.db')
#     df.to_sql('advertising_db',connection,index=False,if_exists='replace')
#     connection.close()

# #cursor = connection.cursor()
# cursor.execute(f"CREATE TABLE IF NOT EXISTS {Advertising} (TV INTEGER, radio REAL, newspaper REAL, sales REAL);")

@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"

# 1. Endpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada

# @app.route('/v2/predict', methods=['GET'])
# def predict():
#     connection=sqlite3.connect('data/Advertising.db')
#     curs=connection.cursor()
#     curs.execute('SELECT * FROM Advertising')
#     advertising = curs.fetchall()
#     connection.close()
#     model = pickle.load(open('data/advertising_model','rb'))

#     tv = request.args.get('TV', None)
#     radio = request.args.get('radio', None)
#     newspaper = request.args.get('newspaper', None)

#     if tv is None or radio is None or newspaper is None:
#         return "Missing args, the input values are needed to predict"
#     else:
#         prediction = model.predict([[int(tv),int(radio),int(newspaper)]])
#         return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'


# stv
@app.route('/v2/predict', methods=['GET'])
def predict_list():
    model = pickle.load(open('data/advertising_model','rb'))
    data = request.get_json()   #{"data": [[100, 100, 200]]}

    input_values = data['data'][0]
    tv, radio, newspaper = map(int, input_values)

    prediction = model.predict([[tv, radio, newspaper]])
    return jsonify({'prediction': round(prediction[0], 2)})



#2
# @app.route('/v2/ingest_data',methods=['POST'])
# def ingest_data():
#     data = request.get_json()
    
#     connection = sqlite3.connect('data/Advertising.db')
#     curs=connection.cursor()

#     curs.execute("INSERT INTO Advertising (TV, radio, newspaper, sales) VALUES (?, ?, ?,?)",
#                  (data['TV'], data['radio'], data['newspaper'], data['sales']))
#     connection.commit()
#     connection.close()
#     return 'Data updated'

#stv
@app.route('/v2/ingest_data', methods=['POST'])
def add_data():
    data = request.get_json()

    for row in data.get('data', []):
        tv, radio, newspaper, sales = row
        query = "INSERT INTO Advertising (tv, radio, newspaper, sales) VALUES (?, ?, ?, ?)"
        connection = sqlite3.connect('data/Advertising.db')
        crsr = connection.cursor()
        crsr.execute(query, (tv, radio, newspaper, sales))
        connection.commit()
        connection.close()

    return jsonify({'message': 'Updated data successfully'})


#3
# @app.route('/v2/retrain',methods=['POST'])
# def retrain():
#     connection = sqlite3.connect('data/Advertising.db')
#     query="SELECT * FROM Advertising"
#     df=pd.read_sql_query(query,connection)
#     connection.close()

#     X=df[['TV','radio','newspaper']]
#     y=df['sales']

#     model = pickle.load(open('data/advertising_model','rb'))

#     model.fit(X,y)
#     with open('data/advertising_model', 'wb') as file:
#         pickle.dump(model, file)
#     return "Model trained successfully"

#stv
@app.route('/v2/retrain', methods=['POST'])
def retrain():
    conn = sqlite3.connect('data/Advertising.db')
    crsr = conn.cursor()
    query = "SELECT * FROM Advertising;"
    crsr.execute(query)
    ans = crsr.fetchall()
    conn.close()
    names = [description[0] for description in crsr.description]
    df = pd.DataFrame(ans, columns=names)
    model = pickle.load(open('data/advertising_model', 'rb'))
    X = df[["TV", "newspaper", "radio"]]
    y = df["sales"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=10)
    model.fit(X_train, y_train)
    pickle.dump(model, open('advertising_model_2', 'wb'))

    return jsonify({'message': 'Model retrained correctly'})


app.run()