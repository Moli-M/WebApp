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
    """
    Registro de un nuevo usuario
    ---
    get:
      description: Muestra la página de registro de usuario
      responses:
        200:
          description: Página de registro mostrada con éxito

    post:
      description: Registra un nuevo usuario
      parameters:
        - name: username
          in: formData
          type: string
          required: true
          description: Nombre de usuario
        - name: password
          in: formData
          type: string
          required: true
          description: Contraseña del usuario
        - name: confirm_password
          in: formData
          type: string
          required: true
          description: Confirmación de la contraseña del usuario
        - name: name
          in: formData
          type: string
          required: true
          description: Nombre completo del usuario
        - name: email
          in: formData
          type: string
          required: true
          description: Correo electrónico del usuario
      responses:
        200:
          description: Usuario registrado con éxito
        400:
          description: Error en los datos de entrada
        409:
          description: Conflicto, el usuario o el correo electrónico ya existen
    """
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
    """
    Inicio de sesión de usuario
    ---
    get:
    description: Muestra la página de inicio de sesión
    responses:
        200:
        description: Página de inicio de sesión mostrada con éxito

    post:
    description: Autentica a un usuario
    parameters:
        - name: username
        in: formData
        type: string
        required: true
        description: Nombre de usuario
        - name: password
        in: formData
        type: string
        required: true
        description: Contraseña del usuario
    responses:
        200:
        description: Usuario autenticado con éxito
        400:
        description: Error en los datos de entrada
        401:
        description: Credenciales incorrectas
    """

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
    """
    Cierre de sesión de usuario
    ---
    post:
    description: Cierra la sesión del usuario autenticado
    responses:
        200:
        description: Usuario desconectado con éxito
        401:
        description: Usuario no autenticado
    """

    borrar_graficos()
    logout_user()
    return redirect(url_for('userController.login'))

@userController.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    Restablecimiento de contraseña
    ---
    get:
    description: Muestra la página para restablecer la contraseña
    responses:
        200:
        description: Página de restablecimiento de contraseña mostrada con éxito

    post:
    description: Permite a un usuario restablecer su contraseña
    parameters:
        - name: email
        in: formData
        type: string
        required: true
        description: Correo electrónico del usuario
        - name: new_password
        in: formData
        type: string
        required: true
        description: Nueva contraseña del usuario
        - name: confirm_new_password
        in: formData
        type: string
        required: true
        description: Confirmación de la nueva contraseña del usuario
    responses:
        200:
        description: Contraseña restablecida con éxito
        400:
        description: Error en los datos de entrada
        404:
        description: Usuario no encontrado
        409:
        description: Las contraseñas no coinciden
    """

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
    """
    Perfil del usuario
    ---
    get:
    description: Muestra la página de perfil del usuario autenticado
    responses:
        200:
        description: Página de perfil mostrada con éxito
        401:
        description: Usuario no autenticado

    post:
    description: Actualiza el perfil del usuario autenticado
    responses:
        200:
        description: Perfil actualizado con éxito
        400:
        description: Error en los datos de entrada
        401:
        description: Usuario no autenticado
    """

    data={
        'titulo': 'Perfil',
        'usuario': current_user
    }
    return render_template('profile.html', data=data)

@userController.route('/update_profile', methods=['POST', 'GET'])
@login_required
def update_profile():
    """
    Actualización del perfil del usuario
    ---
    get:
    description: Muestra la página para actualizar el perfil del usuario autenticado
    responses:
        200:
        description: Página de actualización de perfil mostrada con éxito
        401:
        description: Usuario no autenticado

    post:
    description: Actualiza el perfil del usuario autenticado
    parameters:
        - name: name
        in: formData
        type: string
        required: true
        description: Nombre completo del usuario
        - name: password
        in: formData
        type: string
        required: false
        description: Nueva contraseña del usuario (opcional)
        - name: confirm_password
        in: formData
        type: string
        required: false
        description: Confirmación de la nueva contraseña del usuario (opcional)
    responses:
        200:
        description: Perfil actualizado con éxito
        400:
        description: Error en los datos de entrada
        401:
        description: Usuario no autenticado
        409:
        description: Las contraseñas no coinciden
    """

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

@userController.route('/delete_user', methods=['POST', 'DELETE', 'GET'])
@login_required
def delete_user():
    """
    Eliminación de cuenta de usuario
    ---
    get:
    description: Muestra la página para eliminar la cuenta de usuario
    responses:
        200:
        description: Página de eliminación de cuenta mostrada con éxito
        401:
        description: Usuario no autenticado

    post:
    description: Elimina la cuenta del usuario autenticado
    parameters:
        - name: user_id
        in: formData
        type: integer
        required: true
        description: ID del usuario a eliminar
    responses:
        200:
        description: Usuario eliminado con éxito
        400:
        description: Error en los datos de entrada
        401:
        description: Usuario no autenticado
        403:
        description: No tienes permiso para eliminar esta cuenta
        404:
        description: Usuario no encontrado

    delete:
    description: Elimina la cuenta del usuario autenticado
    parameters:
        - name: user_id
        in: formData
        type: integer
        required: true
        description: ID del usuario a eliminar
    responses:
        200:
        description: Usuario eliminado con éxito
        400:
        description: Error en los datos de entrada
        401:
        description: Usuario no autenticado
        403:
        description: No tienes permiso para eliminar esta cuenta
        404:
        description: Usuario no encontrado
    """

    user_id = request.form['user_id']
    if current_user.id != int(user_id):
        flash('No tienes permiso para eliminar esta cuenta.', 'error')
        return redirect(url_for('userController.profile'))

    user = User.query.get(user_id)
    
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado con éxito.', 'success')
        return redirect(url_for('userController.logout'))
    else:
        flash('Usuario no encontrado.', 'error')
    
    return redirect(url_for('userController.login'))