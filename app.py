import os
import pika
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
from queue import Queue

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins='*')

# Variables globales
connection = None
channel = None
message_queue = Queue()  # Cola para almacenar los mensajes recibidos

# Configura la conexión con RabbitMQ
def connect_rabbitmq():
    global connection, channel
    credentials = pika.PlainCredentials('user', 'QF1DCB!GYWpJ')
    parameters = pika.ConnectionParameters(host='20.232.116.211', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='my_queue')

def callback(ch, method, properties, body):
    message = body.decode()
    print("Mensaje recibido: " + message)
    message_queue.put(message)  # Almacena el mensaje en la cola

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
    except pika.exceptions.AMQPConnectionError:
        print("Error: No se pudo conectar a RabbitMQ.")

def send_queued_messages():
    while True:
        message = message_queue.get()  # Obtiene un mensaje de la cola
        socketio.emit('message', message)  # Envía el mensaje a los clientes conectados

def start_consuming():
    print("Consumiendo mensajes...")
    channel.basic_consume(queue='my_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    connect_rabbitmq()  # Establece la conexión al iniciar el programa
    
    # Crea un hilo para el consumo de mensajes
    consuming_thread = threading.Thread(target=start_consuming)
    consuming_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
    consuming_thread.start()
    
    # Crea un hilo para enviar los mensajes encolados
    send_messages_thread = threading.Thread(target=send_queued_messages)
    send_messages_thread.daemon = True  # El hilo se detendrá cuando el programa principal se cierre
    send_messages_thread.start()
    
    # Ejecuta el socket en el hilo principal
    socketio.run(app)
