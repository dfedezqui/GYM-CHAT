import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from backend.core.analyzer import clasificar
from backend.data.loader import devolver_mensaje


base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'frontend', 'templates')
static_dir = os.path.join(base_dir, 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

socketIO = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketIO.on('message')
def handle_message(msg):
    
    funcion, argumentos = clasificar(msg)

    respuesta = devolver_mensaje(funcion, argumentos)
    
    send(respuesta)

if __name__ == '__main__':
    app.run(debug=True)
