import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User, db
from models.history import History
import subprocess;
import tensorflow as tf
import pandas as pd
import sys
import json
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

import matplotlib.pyplot as plt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'test'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    #return "prueba"
    borrar_graficos()
    data={
        'titulo': 'Index',
        'encabezado': 'Prueba',
        'cont': 0
    }
    return render_template('index.html', data=data)

@app.route('/history')
def history():
    borrar_graficos()
    historiales = History.query.filter_by(uid=current_user.id).all()
    print(historiales)
    data={
        'historiales': historiales,
        'titulo': 'Historial'
    }
    return render_template('history.html', data=data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if(password != confirm_password):
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El usuario ya existe.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            #return 'Login fallido. Por favor, verifica tus credenciales.'
            flash('Login fallido. Por favor, verifica tus credenciales.', 'error')
    data={
        'titulo': 'Inicio de sesión',
    }
    return render_template('login.html', data=data)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    borrar_graficos()
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload')
@login_required
def upload():
    borrar_graficos()
    data={
        'titulo': 'Upload'
    }
    return render_template('upload.html', data=data)

@app.route('/procesar', methods=['POST', 'GET'])
@login_required
def procesar():
    if request.method == 'POST':
        if 'archivo' not in request.files:
            return redirect(url_for('index'))

        archivo = request.files['archivo'] 
        if archivo and (archivo.filename.endswith('.txt') or archivo.filename.endswith('.csv')):
            archivo_path = os.path.join('csv', archivo.filename)
            archivo.save(".\\csv\\"+archivo.filename)
            resultado_script = ejecutar_script(archivo_path)
            print(resultado_script)
            probabilidades = gen_grafico(resultado_script)
            #probabilidades_lista = [str(item) for sublist in resultado_script for item in sublist]
            res = History(result=str(probabilidades), uid=current_user.id)
            db.session.add(res)
            db.session.commit()
            data = {
                'titulo': 'Resultado del script',	
                'cont': 1,
                'archivo': 'img/grafico.png',
                'probabilidades': probabilidades
            }
            return render_template("index.html", data = data)

        return 'Formato de archivo no permitido. Por favor, sube un archivo .txt o .csv.'

@app.route('/prueba', methods=['POST', 'GET'])
@login_required
def prueba():
    data = {
        'titulo': 'Resultado del script',	
        'cont': 1,
        'archivo': 'img/grafico.png'
    }
    return render_template("index.html", data = data)

@app.route('/history/<int:history_id>')
@login_required
def history_details(history_id):
    historial = History.query.get_or_404(history_id)
    
    resultado_script = json.loads(historial.result)
    probabilidades = gen_grafico2(resultado_script)

    data = {
        'titulo': 'Detalles del Historial',
        'historial': historial,
        'archivo': 'static/img/grafico.png',
        'probabilidades': probabilidades,
    }

    return render_template('history_details.html', data=data)


def gen_grafico(datos):
    num_clases = len(datos[0])  # Número de clases
    clases = [f'Clase {i+1}' for i in range(num_clases)]
    probabilidades = [sum(sublista) / len(sublista) for sublista in zip(*datos)]

    # Generar el gráfico de barras
    plt.bar(clases, probabilidades)
    plt.xlabel('Clases')
    plt.ylabel('Probabilidades promedio')
    plt.title('Resultado')

    # Guardar el gráfico en un archivo
    nombre_archivo = 'static/img/grafico.png'
    plt.savefig(nombre_archivo)
    return probabilidades

def gen_grafico2(datos):
    num_clases = len(datos)
    clases = [f'Clase {i+1}' for i in range(num_clases)]
    probabilidades = datos

    # Generar el gráfico de barras
    plt.bar(clases, probabilidades)
    plt.xlabel('Clases')
    plt.ylabel('Probabilidades promedio')
    plt.title('Resultado')

    # Guardar el gráfico en un archivo
    nombre_archivo = 'static/img/grafico.png'
    plt.savefig(nombre_archivo)
    return probabilidades


def ejecutar_script(archivo_path):
    try:
        data=pd.read_csv(archivo_path)
        os.remove(archivo_path)
        modelo = keras.models.load_model('./static/python/modelo_entrenado3.keras')

        X = data.drop('class', axis=1)

        le = LabelEncoder()
        for col in X.select_dtypes(include=['object']):
            X[col] = le.fit_transform(X[col])

        scaler = StandardScaler()
        X[X.select_dtypes(include=['float64']).columns] = scaler.fit_transform(X.select_dtypes(include=['float64']))

        results = modelo.predict(X)
        return results
    except Exception as e:
        return str(e)

def borrar_graficos():
    archivos = os.listdir('static/img')
    for archivo in archivos:
        if archivo.endswith('.png'):
            os.remove(f'static/img/{archivo}')

if __name__ == '__main__':
    app.run(debug=True, port=5005)