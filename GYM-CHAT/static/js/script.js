const socket = io();
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const inputMessage = document.getElementById('input-message');

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');

    if (sender === 'bot') {
        // Renderizar Markdown
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.textContent = text;
    }

    msgDiv.appendChild(bubble);
    chatWindow.appendChild(msgDiv);
    
    // Pequeño delay para asegurar que el DOM cargó el contenido antes de hacer scroll
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