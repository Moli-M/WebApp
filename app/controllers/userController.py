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

userController = Blueprint('userController', __name__, template_folder='templates')



@userController.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        email = request.form['email']

        if(password != confirm_password):
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('userController.register'))

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('El formato del correo electrónico no es válido.', 'error')
            return redirect(url_for('userController.register'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El usuario ya existe.', 'error')
            return redirect(url_for('userController.register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('El correo electrónico ya está en uso.', 'error')
            return redirect(url_for('userController.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('userController.login'))
    return render_template('register.html')

@userController.route('/login', methods=['GET', 'POST'])
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

@userController.route('/logout', methods=['POST'])
@login_required
def logout():
    borrar_graficos()
    logout_user()
    return redirect(url_for('userController.login'))

@userController.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('No se encontró ningún usuario con ese email.', 'error')
            return redirect(url_for('userController.forgot_password'))

        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if(new_password != confirm_new_password):
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('userController.forgot_password'))

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return redirect(url_for('userController.login'))
    
    return render_template('forgot_password.html')

@userController.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    data={
        'titulo': 'Perfil',
        'usuario': current_user
    }
    return render_template('profile.html', data=data)

@userController.route('/update_profile', methods=['POST', 'GET'])
@login_required
def update_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']

        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if(password and confirm_password):
            if(password != confirm_password):
                flash('Las contraseñas no coinciden.', 'error')
                return redirect(url_for('userController.update_profile'))
            current_user.password = generate_password_hash(password)

        db.session.commit()
        return redirect(url_for('userController.profile'))