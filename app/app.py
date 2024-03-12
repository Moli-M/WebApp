import os
from flask import Flask, redirect, render_template, request


app = Flask(__name__)


@app.route('/')
def index():
    #return "prueba"
    
    data={
        'titulo': 'Index',
        'encabezado': 'Prueba'
    }
    return render_template('index.html', data=data)


@app.route('/login')
def login():
    data={
        'titulo': 'Login',
    }
    return render_template('login.html', data=data)

@app.route('/contacto')
def contacto():
    data={
        'titulo': 'Contacto',
        'encabezado': 'Prueba'
    }
    return render_template('contacto.html', data=data)

@app.route('/suma/<int:v1>/<int:v2>')
def suma(v1,v2):
    return '{}'.format(v1 + v2)

@app.route('/datos')
def datos():
    valor1 = request.args.get('v1') 
    return f'LADjfalñsdjflk {valor1}'

@app.route('/lenguajes')
def lenguajes():
    data={
        'titulo': 'Lenguajes',
        'lenguajes':['PHP', 'Python', 'C', 'Java']
    }
    return render_template('lenguajes.html', data=data)

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