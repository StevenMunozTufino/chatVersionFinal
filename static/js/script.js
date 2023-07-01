var socket = io();
let numMensajes = 0;
var idUser = null;

// Función para mostrar el modal al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    $('#modalID').modal({
        backdrop: 'static', // Evita que el modal se cierre al hacer clic fuera de él
        keyboard: false // Evita que el modal se cierre al presionar la tecla Esc
    });
    $('#modalID').modal('show');
});

function guardarID() {

    var inputID = document.getElementById('inputID');
    var idIngresado = inputID.value.trim();

    if (idIngresado !== "") {
        idUser = idIngresado;
        console.log("ID ingresado:", idUser);

        // Cierra el modal después de guardar el ID
        $('#modalID').modal('hide');
    }
}

function fecha(){
    var fechaActual = new Date();
    // Obtener los componentes de la fecha
    var anio = fechaActual.getFullYear();
    var mes = ('0' + (fechaActual.getMonth() + 1)).slice(-2); // Sumar 1 al mes ya que los meses en JavaScript comienzan desde 0
    var dia = ('0' + fechaActual.getDate()).slice(-2);
    return dia +'/'+ mes +'/' + anio;
}

function horaH(){
    var fechaActual = new Date();
    // Obtener los componentes de la hora
    var hora = ('0' + fechaActual.getHours()).slice(-2);
    var minuto = ('0' + fechaActual.getMinutes()).slice(-2);
    var segundo = ('0' + fechaActual.getSeconds()).slice(-2);
    return hora +':' + minuto;    
}

//Función para el envío de mensajes para el texto del textarea
function sendMessage() {
    var message = document.getElementById('message').value;
    if (message.trim() !== '') {
        mensaje = message+'@'+fecha()+ '@'+ horaH() + '@' + idUser;
        socket.emit('message', mensaje); //Envía a la cola
        document.getElementById('message').value = '';
        document.getElementById('message').focus();
    }
}


//WebSocket para escuchar los mensajes recibidos
socket.on('message', function(message) {
    numMensajes ++;
    const numeroElemento = document.getElementById('numero');
    numeroElemento.textContent = numMensajes + ' Mensajes';
    //Descomponer el mensaje
    var datos = message.split('@');
    if (datos[3] == idUser) {
        console.log("Mensaje Enviado");
        var chatBox = document.getElementById('chat-box');
        var messageContainer = document.createElement('div');
        messageContainer.classList.add('d-flex', 'justify-content-end', 'mb-4');

        var textContainer = document.createElement('div');
        textContainer.classList.add('msg_cotainer_send');
        textContainer.textContent = datos[0];

        var timeElement = document.createElement('span');
        timeElement.classList.add('msg_time_send');
        timeElement.textContent = datos[2]+', ' + datos[1]; // Aquí puedes agregar la hora actual del mensaje

        var imgContainer = document.createElement('div');
        imgContainer.classList.add('img_cont_msg');

        var imgElement = document.createElement('img');
        imgElement.src = "../static/images/enviado.png";
        imgElement.classList.add('user_img_msg', 'img_no_border');

        textContainer.appendChild(timeElement);
        imgContainer.appendChild(imgElement);
        messageContainer.appendChild(textContainer);
        messageContainer.appendChild(imgContainer);
        chatBox.appendChild(messageContainer);

        chatBox.scrollTop = chatBox.scrollHeight;
    } else {
        console.log("Mensaje Recibido");
        var chatBox = document.getElementById('chat-box');
        var messageContainer = document.createElement('div');
        messageContainer.classList.add('d-flex', 'justify-content-start', 'mb-4');

        var imgContainer = document.createElement('div');
        imgContainer.classList.add('img_cont_msg');

        var imgElement = document.createElement('img');
        imgElement.src = "../static/images/recibido.png";
        imgElement.classList.add('user_img_msg', 'img_no_border');

        var nameElement = document.createElement('span');
        nameElement.classList.add('msg_name');
        nameElement.textContent = datos[3];

        var textContainer = document.createElement('div');
        textContainer.classList.add('msg_cotainer');
        textContainer.textContent = datos[0];

        var timeElement = document.createElement('span');
        timeElement.classList.add('msg_time');
        timeElement.textContent = datos[2]+', ' + datos[1]; // Aquí puedes agregar la hora actual del mensaje

        textContainer.appendChild(nameElement);
        textContainer.appendChild(timeElement);
        imgContainer.appendChild(imgElement);
        messageContainer.appendChild(imgContainer);
        messageContainer.appendChild(textContainer);
        chatBox.appendChild(messageContainer);

        chatBox.scrollTop = chatBox.scrollHeight;
    }
});

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('message').addEventListener('keydown', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendMessage();
    }
});