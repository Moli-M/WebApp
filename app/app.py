import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'test'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    #return "prueba"
    
    data={
        'titulo': 'Index',
        'encabezado': 'Prueba'
    }
    return render_template('index.html', data=data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Login fallido. Por favor, verifica tus credenciales.'
    data={
        'titulo': 'Login',
    }
    return render_template('login.html', data=data)

@app.route('/upload')
def upload():
    data={
        'titulo': 'Upload'
    }
    return render_template('upload.html', data=data)

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'archivo' not in request.files:
        return redirect(request.url)

    archivo = request.files['archivo']

    if archivo.filename == '':
        return redirect(request.url)

    if archivo and archivo.filename.endswith('.txt'):
        # Guardar el archivo temporalmente
        archivo_path = os.path.join('archivos_temporales', archivo.filename)
        archivo.save(archivo_path)

        # Ejecutar el script de Python con el archivo como argumento
        resultado_script = ejecutar_script(archivo_path)

        # Puedes hacer algo con el resultado del script, como mostrarlo en la página

        return f'Resultado del script: {resultado_script}'

    return 'Formato de archivo no permitido. Por favor, sube un archivo .txt.'

def ejecutar_script(archivo_path):
    # Aquí puedes ejecutar el script de Python que quieras
    # En este caso, simplemente leemos el archivo y devolvemos su contenido
    with open(archivo_path, 'r') as archivo:
        return archivo.read()
    

if __name__ == '__main__':
    app.run(debug=True, port=5005)