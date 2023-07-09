import os
import pika
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app,cors_allowed_origins='*')
CORS(app)

connection = None
channel = None

# Configura la conexión con RabbitMQ
def connect_rabbitmq():
    global connection, channel
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()





@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('usuario')
def handle_login(id):
    pass
   

#Conexion y desconexión de clientes
#####################################################################################################################

@socketio.on('connect')
def handle_connect():
    connect_rabbitmq()  # Intenta conectarse a RabbitMQ

@socketio.on('disconnect')
def handle_disconnect():
    global connection, channel

    if connection and connection.is_open:
        connection.close()
   

@socketio.on('message')
def handle_message(data):
    mensaje=data['message']
    enviarA=data['enviarA']
    print("enviarA: ",enviarA)
    try:
        # Verifica si la conexión con RabbitMQ está abierta
        if not connection or not connection.is_open:
            connect_rabbitmq()  # Intenta reconectarse si no hay conexión o la conexión está cerrada
        # Envía el mensaje a la cola de RabbitMQ
        channel.basic_publish(exchange='', routing_key=enviarA, body=mensaje)
    except pika.exceptions.AMQPConnectionError as e:
        
        print("Mensaje de error real:", str(e))

@socketio.on('pedirMensajes')
def handle_recibir(perfil):
    if perfil != None:
        method_frame, _, body = channel.basic_get(queue=perfil, auto_ack=True)
        if method_frame:
            emit('recibir', body.decode(), broadcast=False)
        else:
            pass
    else:
        pass

if __name__ == '__main__':
    socketio.run(app)