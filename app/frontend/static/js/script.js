const socket = io();

const chatWindow = document.getElementById('chat');
const chatForm = document.getElementById('chat-form');
const inputMessage = document.getElementById('input-message');

// Variables de control
let typingElem = null;
let typingInterval = null;

function appendMessage(message, isOwnMessage = false, typingEffect = false) {
    // Si hay una animación previa, detenerla y mostrar todo de golpe
    if (typingInterval) {
        clearInterval(typingInterval);
        typingInterval = null;
        if (typingElem) {
            typingElem.textContent = typingElem.dataset.fullMessage || '';
            typingElem = null;
        }
    }

    const msgElem = document.createElement('p');
    msgElem.classList.add('message');

    if (isOwnMessage) {
        msgElem.classList.add('user');
        msgElem.textContent = message;
    } else {
        msgElem.classList.add('bot');

        if (typingEffect) {
            msgElem.textContent = '';
            msgElem.dataset.fullMessage = message; // Guarda el texto completo por si hay que mostrarlo directamente

            let i = 0;
            typingInterval = setInterval(() => {
                msgElem.textContent += message[i];
                i++;
                chatWindow.scrollTop = chatWindow.scrollHeight;

                if (i >= message.length) {
                    clearInterval(typingInterval);
                    typingInterval = null;
                    typingElem = null;
                }
            }, 25);

            typingElem = msgElem; // Guardamos el mensaje que se está escribiendo
        } else {
            msgElem.textContent = message;
        }
    }

    chatWindow.appendChild(msgElem);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return msgElem;
}

// Cuando recibimos un mensaje del servidor
socket.on('message', function (data) {
    // Eliminar "escribiendo..." si está
    if (typingElem && typingElem.textContent === 'Escribiendo...') {
        typingElem.remove();
        typingElem = null;
    }

    // Mostrar mensaje con efecto tipo "máquina de escribir"
    appendMessage(data, false, true);
});

// Cuando enviamos un mensaje
chatForm.addEventListener('submit', function (event) {
    event.preventDefault();
    const message = inputMessage.value.trim();

    if (message.length > 0) {
        // Enviar al servidor
        socket.send(message);

        // Mostrar localmente
        appendMessage(message, true);

        inputMessage.value = '';
        inputMessage.focus();

        // Mostrar el "Escribiendo..." del bot
        if (typingInterval) {
            clearInterval(typingInterval);
            typingInterval = null;
        }
        if (typingElem) {
            typingElem.remove();
        }

        typingElem = document.createElement('p');
        typingElem.classList.add('message', 'bot', 'typing');
        typingElem.textContent = 'Escribiendo...';
        chatWindow.appendChild(typingElem);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
