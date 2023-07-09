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

consuming_thread = None

perfil = None
connection = None
channel = None
connectionRecibir = None
channelRecibir = None
client_id = None
cola = deque()

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
    global perfil, consuming_thread
    perfil = id
    
    print("perfil: ",perfil)
    consuming_thread = threading.Thread(target=start_consuming)
    consuming_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
    consuming_thread.start()
   

#Conexion y desconexión de clientes
#####################################################################################################################

@socketio.on('connect')
def handle_connect():
    global client_id
    connect_rabbitmq()  # Intenta conectarse a RabbitMQ
    connect_rabbitmqRecibir()

@socketio.on('disconnect')
def handle_disconnect():
    global consuming_thread
    global connection, channel
    try:
        if connection and connection.is_open:
            connection.close()
            connectionRecibir.close()        
        consuming_thread.join()  # Detener el hilo si existe
        consuming_thread = None
        
    except pika.exceptions.AMQPConnectionError as e:
        handle_disconnect()
   

@socketio.on('message')
def handle_message(data):
    mensaje=data['message']
    enviarA=data['enviarA']
    
    try:
        # Verifica si la conexión con RabbitMQ está abierta
        if not connection or not connection.is_open:
            connect_rabbitmq()  # Intenta reconectarse si no hay conexión o la conexión está cerrada
        # Envía el mensaje a la cola de RabbitMQ

        channel.basic_publish(exchange='', routing_key=enviarA, body=mensaje)
    except pika.exceptions.AMQPConnectionError as e:
        
        print("Mensaje de error real:", str(e))

@socketio.on('recibir')
def handle_recibir():
    global cola

    if len(cola)>0:
        print(request.sid)      
        emit('recibir', {'mensaje':cola.popleft(),'id':request.sid})


#Para recibir mensajes

def start_consuming():
    global connectionRecibir, channelRecibir, perfil
    try:
        
        print("Consumiendo mensajes..."+perfil)
        channelRecibir.basic_consume(queue=perfil, on_message_callback=callback, auto_ack=True)
        channelRecibir.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("Error de conexión RabbitMQ:", str(e))
        connect_rabbitmqRecibir()


def callback(ch, method, properties, body):
    global client_id, cola

    message = body.decode()
    print("Mensaje recibido: " + message)
    cola.append(message)


if __name__ == '__main__':
    socketio.run(app)