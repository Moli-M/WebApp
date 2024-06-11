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
import re
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from flask_migrate import Migrate
import matplotlib.pyplot as plt
from utils import gen_grafico, gen_grafico2, ejecutar_script, borrar_graficos
from controllers.userController import userController
from controllers.dataController import dataController

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'test'

db.init_app(app)

migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.register_blueprint(userController, url_prefix='/user')
app.register_blueprint(dataController, url_prefix='/data')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    borrar_graficos()
    data={
        'titulo': 'Index',
        'encabezado': 'Prueba',
        'cont': 0
    }
    return render_template('index.html', data=data)

@app.route('/prueba', methods=['POST', 'GET'])
@login_required
def prueba():
    data = {
        'titulo': 'Resultado del script',	
        'cont': 1,
        'archivo': 'img/grafico.png'
    }
    return render_template("index.html", data = data)


if __name__ == '__main__':
    app.run(debug=True, port=5005)