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