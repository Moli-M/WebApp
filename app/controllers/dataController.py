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

@dataController.route('/procesar', methods=['POST', 'GET'])
@login_required
def procesar():
    """
    Procesa un archivo enviado por el usuario y muestra los resultados.
    ---
    tags:
        - Data
    parameters:
      - name: archivo
        in: formData
        type: file
        required: true
        description: Archivo (formato .txt o .csv) a procesar.

    responses:
      200:
        description: Resultados del procesamiento mostrados correctamente.
        schema:
          type: object
          properties:
            titulo:
              type: string
              description: Título de la página
            cont:
              type: integer
              description: Contador inicializado en 1
            archivo:
              type: string
              description: Ruta del archivo generado (imagen)
            probabilidades:
              type: object
              description: Resultados de probabilidades generados
    """


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

@dataController.route('/history/<int:history_id>', methods=['POST', 'GET', 'DELETE'])
@login_required
def history_details(history_id):
    """
    Obtiene los detalles del historial especificado por su ID.
    ---
    tags:
        - Data
    parameters:
      - name: history_id
        in: path
        type: integer
        required: true
        description: ID del historial a obtener.

    responses:
      200:
        description: Detalles del historial obtenidos correctamente.
        schema:
        type: object
        properties:
            titulo:
              type: string
              description: Título de la página
            historial:
              type: object
              description: Detalles del historial
            archivo:
              type: string
              description: Ruta del archivo generado (imagen)
            probabilidades:
              type: object
              description: Resultados de probabilidades generados
      404:
        description: Historial no encontrado.
    """

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


@dataController.route('/history')
@login_required
def history():
    """
    Obtiene el historial de procesamientos del usuario actual.
    ---
    tags:
        - Data
    responses:
      200:
        description: Historial obtenido correctamente.
        schema:
        type: object
        properties:
            titulo:
              type: string
              description: Título de la página
            historiales:
              type: array
              items:
                type: object
                properties:
                id:
                    type: integer
                    description: ID del historial
                result:
                    type: string
                    description: Resultado del procesamiento
                uid:
                    type: integer
                    description: ID del usuario
    """


    borrar_graficos()
    historiales = History.query.filter_by(uid=current_user.id).all()
    print(historiales)
    data={
        'historiales': historiales,
        'titulo': 'Historial'
    }
    return render_template('history.html', data=data)

@dataController.route('/history/delete/<int:history_id>', methods=['POST', 'GET', 'DELETE'])
@login_required
def delete_history(history_id):
    """
    Elimina un historial especificado por su ID.
    ---
    tags:
        - Data
    parameters:
      - name: history_id
        in: path
        type: integer
        required: true
        description: ID del historial a eliminar.

    responses:
      200:
        description: Historial eliminado correctamente.
      404:
        description: Historial no encontrado.
    """

    historial = History.query.get_or_404(history_id)
    db.session.delete(historial)
    db.session.commit()
    return redirect(url_for('dataController.history'))