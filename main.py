import os
import pika
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Configura la conexión con RabbitMQ
credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declara una cola para recibir mensajes
channel.queue_declare(queue='my_queue')

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('message')
def handle_message(message):
    # Envía el mensaje a la cola de RabbitMQ
    channel.basic_publish(exchange='', routing_key='my_queue', body=message)
    emit('message', message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
