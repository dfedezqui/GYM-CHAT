const socket = io();

const chatWindow = document.getElementById('chat');
const chatForm = document.getElementById('chat-form');
const inputMessage = document.getElementById('input-message');

function appendMessage(message, isOwnMessage = false) {
    const msgElem = document.createElement('p');
    msgElem.textContent = message;
    msgElem.classList.add('message');
    if(isOwnMessage) {
        msgElem.classList.add('user');
    } else {
        msgElem.classList.add('bot');
    }
    chatWindow.appendChild(msgElem);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


// Cuando recibimos un mensaje desde el servidor
socket.on('message', function(data) {
    // Opcional: evitar mostrar el mensaje que tú acabas de enviar si ya lo pusiste localmente
    appendMessage(data, false);
});

// Cuando enviamos un mensaje
chatForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const message = inputMessage.value.trim();
    if(message.length > 0){
        socket.send(message);
        appendMessage(message, true);  // Añade el mensaje localmente como propio
        inputMessage.value = '';
        inputMessage.focus();
    }
});
