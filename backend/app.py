import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from core.analyzer import clasificar
from data.loader import devolver_mensaje

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)  
template_dir = os.path.join(project_root, 'frontend', 'templates')
static_dir = os.path.join(project_root, 'frontend', 'static')

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
    port = int(os.environ.get('PORT', 5000))
    socketIO.run(app, host='0.0.0.0', port=port)
