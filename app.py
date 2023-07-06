import os
import pika
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
from flask_cors import CORS

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app,cors_allowed_origins='*')
CORS(app)

consuming_thread = None

# Variables globales
connection = None
channel = None
usuario = None

# Configura la conexión con RabbitMQ
def connect_rabbitmq():
    global connection, channel
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()


def callback(ch, method, properties, body):
    message = body.decode()
    print("Mensaje recibido: " + message)
    socketio.emit('message', message)  # Envía el mensaje a los clientes conectados
    #message_queue.put(message)  # Almacena el mensaje en la cola

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('usuario')
def handle_connect_usuario(cliente):
    global usuario
    global consuming_thread
    usuario = cliente
    connect_rabbitmq()
    consuming_thread = threading.Thread(target=start_consuming)
    consuming_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
    consuming_thread.start()

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('disconnect')
def handle_disconnect():
    global consuming_thread
    global connection
    if consuming_thread is not None:
        connection.close()
        consuming_thread.join()  # Detener el hilo si existe
        consuming_thread = None


@socketio.on('message')
def handle_message(message):

    try:

        # Verifica si la conexión con RabbitMQ está abierta
        if not connection or not connection.is_open:

            connect_rabbitmq()  # Intenta reconectarse si no hay conexión o la conexión está cerrada

        # Envía el mensaje a la cola de RabbitMQ
        if usuario != "Leon":
            channel.basic_publish(exchange='', routing_key='Leon', body=message)
        if usuario != "Mapache":
            channel.basic_publish(exchange='', routing_key='Mapache', body=message)
        if usuario != "Zorro":
            channel.basic_publish(exchange='', routing_key='Zorro', body=message)

        emit('message', message, broadcast=True)  # Envía el mensaje a los clientes conectados

    except pika.exceptions.AMQPConnectionError as e:
        
        print("Mensaje de error real:", str(e))


def start_consuming():
    while True:
        try:
            print("Consumiendo mensajes...")
            if usuario == "Leon":
                channel.basic_consume(queue='Leon', on_message_callback=callback, auto_ack=True)
            if usuario == "Mapache":
                channel.basic_consume(queue='Mapache', on_message_callback=callback, auto_ack=True)
            if usuario == "Zorro":
                channel.basic_consume(queue='Zorro', on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print("Error de conexión RabbitMQ:", str(e))
                # Intenta reconectarse
            connect_rabbitmq()

if __name__ == '__main__':
    socketio.run(app)
