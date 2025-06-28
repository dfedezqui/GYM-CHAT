import eventlet
import os
import sys
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from core.analyzer import clasificar
from data.loader import devolver_mensaje
arg = False
if len(sys.argv) > 1:
    arg = True

if arg:
    eventlet.monkey_patch()

base_dir = os.path.dirname(os.path.abspath(__file__)) 
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

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
    if arg:
        port = int(os.environ.get('PORT', 5000))
        socketIO.run(app, host='0.0.0.0', port=port)
    else:
        socketIO.run(app, debug=True)


