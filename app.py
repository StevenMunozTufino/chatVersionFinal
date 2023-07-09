import os
import pika
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO
import threading
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from collections import deque

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app,cors_allowed_origins='*')
CORS(app)

perfil = None
connection = None
channel = None
connectionRecibir = None
channelRecibir = None
client_id = None


# Configura la conexión con RabbitMQ
def connect_rabbitmq():
    global connection, channel
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

def connect_rabbitmqRecibir():
    global connectionRecibir, channelRecibir
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connectionRecibir = pika.BlockingConnection(parameters)
    channelRecibir = connectionRecibir.channel()



@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('usuario')
def handle_login(id):
    pass
    # consuming_thread = threading.Thread(target=start_consuming)
    # consuming_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
    # consuming_thread.start()
   

#Conexion y desconexión de clientes
#####################################################################################################################

@socketio.on('connect')
def handle_connect():
    global client_id,cola
    session_id = session.get('session_id')  # Obtener el identificador de sesión del usuario
    client_id =session_id
    join_room(session_id)
    connect_rabbitmq()  # Intenta conectarse a RabbitMQ
    connect_rabbitmqRecibir()

@socketio.on('disconnect')
def handle_disconnect():
    global consuming_thread
    global connection, channel
    session_id = session.get('session_id')  # Obtener el identificador de sesión del usuario
    leave_room(session_id) 
    try:
        if connection and connection.is_open:
            connection.close()
            connectionRecibir.close()        

        
    except pika.exceptions.AMQPConnectionError as e:
        handle_disconnect()
   

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
        method_frame, _, body = channelRecibir.basic_get(queue=perfil, auto_ack=True)
        if method_frame:
                # Procesa el mensaje aquí
            print("Mensaje recibido: " + body.decode())
            emit('recibir', body.decode(), broadcast=False)
        else:
                # No se encontraron mensajes en la cola en este momento
            print("No hay mensajes en la cola.")
    else:
        print("perfil es None")  

if __name__ == '__main__':
    socketio.run(app)