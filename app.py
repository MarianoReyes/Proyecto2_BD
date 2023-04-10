from flask import Flask, render_template, request

app = Flask(__name__)

# Define la estructura de datos para simular los archivos hfile
file_data = {}

# Define la ruta para la página principal


@app.route('/')
def index():
    return render_template('index.html', file_data=file_data)

# Define la ruta para crear un nuevo archivo hfile


@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    content = request.form['content']
    file_data[name] = content
    return 'Archivo creado exitosamente!'

# Define la ruta para leer un archivo hfile


@app.route('/read/<name>')
def read(name):
    if name in file_data:
        return file_data[name]
    else:
        return 'El archivo no existe.'

# Define la ruta para actualizar un archivo hfile


@app.route('/update/<name>', methods=['POST'])
def update(name):
    if name in file_data:
        content = request.form['content']
        file_data[name] = content
        return 'Archivo actualizado exitosamente!'
    else:
        return 'El archivo no existe.'

# Define la ruta para eliminar un archivo hfile


@app.route('/delete/<name>', methods=['POST'])
def delete(name):
    if name in file_data:
        del file_data[name]
        return 'Archivo eliminado exitosamente!'
    else:
        return 'El archivo no existe.'


if __name__ == '__main__':
    app.run()
