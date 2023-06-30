from gevent import monkey
monkey.patch_all()

import os
import pika
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, async_mode="gevent",cors_allowed_origins='*')

# Variables globales
connection = None
channel = None

# Configura la conexión con RabbitMQ
def connect_rabbitmq():
    global connection, channel
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='my_queue')

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('message')
def handle_message(message):
    try:
        # Verifica si la conexión con RabbitMQ está abierta
        if not connection or not connection.is_open:
            connect_rabbitmq()  # Intenta reconectarse si no hay conexión o la conexión está cerrada
        
        # Envía el mensaje a la cola de RabbitMQ
        channel.basic_publish(exchange='', routing_key='my_queue', body=message)
        emit('message', message, broadcast=True)
    except pika.exceptions.AMQPConnectionError:
        print("Error: No se pudo conectar a RabbitMQ.")

if __name__ == '__main__':
    connect_rabbitmq()  # Establece la conexión al iniciar el programa
    socketio.run(app, port=5000,debug=True)