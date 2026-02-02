const socket = io();
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const inputMessage = document.getElementById('input-message');

// Variable global para controlar la interrupción
let currentTypewriterTimeout = null;

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function typeWriter(element, text) {
    let i = 0;
    const speed = 15;

    // Si ya hay una escritura en curso, la cancelamos
    if (currentTypewriterTimeout) {
        clearTimeout(currentTypewriterTimeout);
    }

    function type() {
        if (i < text.length) {
            const currentText = text.substring(0, i + 1);
            element.innerHTML = marked.parse(currentText);
            i++;
            scrollToBottom();
            // Guardamos el ID del timeout actual
            currentTypewriterTimeout = setTimeout(type, speed);
        } else {
            // Al terminar, limpiamos la variable
            currentTypewriterTimeout = null;
        }
    }
    type();
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');

    if (sender === 'bot') {
        const icon = document.createElement('span');
        icon.classList.add('bot-icon');
        icon.textContent = '⚡';
        msgDiv.appendChild(icon);
        msgDiv.appendChild(bubble);
        chatWindow.appendChild(msgDiv);
        
        typeWriter(bubble, text);
    } else {
        // Al enviar un mensaje nuevo el usuario, también forzamos la parada de la escritura del bot
        if (currentTypewriterTimeout) {
            clearTimeout(currentTypewriterTimeout);
            currentTypewriterTimeout = null;
        }
        
        bubble.textContent = text;
        msgDiv.appendChild(bubble);
        chatWindow.appendChild(msgDiv);
    }
    
    setTimeout(scrollToBottom, 50);
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = inputMessage.value.trim();
    if (message) {
        appendMessage(message, 'user');
        socket.emit('message', message);
        inputMessage.value = '';
    }
});

socket.on('message', (msg) => {
    appendMessage(msg, 'bot');
});