import os
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User, db
from models.history import History
import subprocess;
import tensorflow as tf
import pandas as pd
import sys
import json
import re
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from flask_migrate import Migrate
import matplotlib.pyplot as plt
from utils import gen_grafico, gen_grafico2, ejecutar_script, borrar_graficos

dataController = Blueprint('dataController', __name__, template_folder='templates')

@dataController.route('/upload')
@login_required
def upload():
    borrar_graficos()
    data={
        'titulo': 'Upload'
    }
    return render_template('upload.html', data=data)

@dataController.route('/procesar', methods=['POST', 'GET'])
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

@dataController.route('/history/<int:history_id>')
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