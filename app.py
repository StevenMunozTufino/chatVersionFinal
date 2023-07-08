import os
import pika
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
from flask_cors import CORS

app = Flask(__name__)
# app.logger.setLevel(logging.WARNING)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app,cors_allowed_origins='*')
CORS(app)

consuming_thread = None
consuming_threadM = None
consuming_threadZ = None
# Variables globales
perfil = None
connection = None
channel = None
connectionRecibir = None
channelRecibir = None
client_id = None
hilo=True

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
    global consuming_thread,consuming_threadM, perfil
    perfil = id
    if perfil == "Leon":
        consuming_thread = threading.Thread(target=start_consuming)
        consuming_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
        consuming_thread.start()
    if perfil == "Mapache":
        consuming_threadM = threading.Thread(target=start_consuming)
        consuming_threadM.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
        consuming_threadM.start()
    if perfil == "Zorro":
        consuming_threadZ = threading.Thread(target=start_consuming)
        consuming_threadZ.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
        consuming_threadZ.start()

#Conexion y desconexión de clientes
#####################################################################################################################
@socketio.on('connect')
def handle_connect():
    global client_id
    client_id = request.sid
    connect_rabbitmq()  # Intenta conectarse a RabbitMQ
    connect_rabbitmqRecibir()

@socketio.on('disconnect')
def handle_disconnect():
    global consuming_thread, consuming_threadM, consuming_threadZ, perfil
    global connection, channel, hilo
    hilo=False
    try:
        if connection and connection.is_open:
            connection.close()
            connectionRecibir.close()        
        if perfil == "Leon":
            consuming_thread.join()  # Detener el hilo si existe
            consuming_thread = None
        if perfil == "Mapache":
            consuming_threadM.join()  # Detener el hilo si existe
            consuming_threadM = None            
        if perfil == "Zorro":
            consuming_threadZ.join()  # Detener el hilo si existe
            consuming_threadZ = None
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

        #emit('message', message, broadcast=True)  # Envía el mensaje a los clientes conectados

    except pika.exceptions.AMQPConnectionError as e:
        
        print("Mensaje de error real:", str(e))

#Para recibir mensajes

def start_consuming():
    global connectionRecibir, channelRecibir, perfil,hilo

    try:
        print("Consumiendo mensajes...")
        channelRecibir.basic_consume(queue=perfil, on_message_callback=callback, auto_ack=True)
        channelRecibir.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("Error de conexión RabbitMQ:", str(e))
                # Intenta reconectarse
        connect_rabbitmqRecibir()


def callback(ch, method, properties, body):
    global client_id

    message = body.decode()
    print("Mensaje recibido: " + message)
    socketio.send('message', message,room = client_id)

if __name__ == '__main__':
    socketio.run(app)