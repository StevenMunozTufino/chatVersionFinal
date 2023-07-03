import os
import pika
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
from flask_cors import CORS

app = Flask(__name__)
# app.logger.setLevel(logging.WARNING)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app,cors_allowed_origins='*')

consuming_thread = None

# Variables globales
connection = None
connectionRecibir = None
channel = None
channelRecibir = None
#message_queue = Queue()  # Cola para almacenar los mensajes recibidos

# Configura la conexión con RabbitMQ
def connect_rabbitmq():
    global connection, channel
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='steven')

def connect_rabbitmqRecibir():
    global connectionRecibir, channelRecibir
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connectionRecibir = pika.BlockingConnection(parameters)
    channelRecibir = connectionRecibir.channel()
    channel.queue_declare(queue='alexander')


def callback(ch, method, properties, body):
    message = body.decode()
    print("Mensaje recibido: " + message)
    socketio.emit('message', message)  # Envía el mensaje a los clientes conectados
    #message_queue.put(message)  # Almacena el mensaje en la cola

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global consuming_thread
    connect_rabbitmqRecibir()
    consuming_thread = threading.Thread(target=start_consuming)
    consuming_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
    consuming_thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    global consuming_thread
    if consuming_thread is not None:
        consuming_thread.join()  # Detener el hilo si existe

@socketio.on('message')
def handle_message(message):
    connect_rabbitmq()
    try:

        # Verifica si la conexión con RabbitMQ está abierta
        if not connection or not connection.is_open:

            connect_rabbitmq()  # Intenta reconectarse si no hay conexión o la conexión está cerrada


        # Envía el mensaje a la cola de RabbitMQ
        channel.basic_publish(exchange='', routing_key='steven', body=message)

        emit('message', message, broadcast=True)  # Envía el mensaje a los clientes conectados

    except pika.exceptions.AMQPConnectionError as e:
        
        print("Mensaje de error real:", str(e))


# def send_queued_messages():
#     while True:
#         message = message_queue.get()  # Obtiene un mensaje de la cola
        

def start_consuming():
    while True:
        try:
            print("Consumiendo mensajes...")
            channelRecibir.basic_consume(queue='alexander', on_message_callback=callback, auto_ack=True)
            channelRecibir.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print("Error de conexión RabbitMQ:", str(e))
            # Intenta reconectarse
            connect_rabbitmqRecibir()

if __name__ == '__main__':
    socketio.run(app)

