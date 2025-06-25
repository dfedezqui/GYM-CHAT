import os
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit


base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'frontend', 'templates')
static_dir = os.path.join(base_dir, 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

socketIO = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketIO.on('message')
def handle_message(data):
    
    mesnaje = "Pronto podre ayudarte con temas de gym"
    

    send(mesnaje)



if __name__ == '__main__':
    app.run(debug=True)
