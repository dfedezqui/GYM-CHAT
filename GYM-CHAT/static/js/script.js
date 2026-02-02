const socket = io();
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const inputMessage = document.getElementById('input-message');

let activeTypewriterId = null;

// --- CONFIGURACIÓN DE TUS LISTAS ---
// text: Lo que ve el usuario en el botón
// value: Lo que se envía a Python (debe coincidir con tu base de datos)
const listaMusculos = [
    { text: "Bíceps", value: "Bíceps" },
    { text: "Tríceps", value: "Tríceps" },
    { text: "Pecho", value: "Pectoral" },
    { text: "Espalda", value: "Dorsal Ancho" },
    { text: "Cuádriceps", value: "Cuádriceps" },
    { text: "Hombro", value: "Deltoides" }
];

const listaEjercicios = [
    { text: "Banca", value: "Press de Banca Plano" },
    { text: "Sentadilla", value: "Sentadilla (Squat)" },
    { text: "Hip Thrust", value: "Empuje de Cadera (Hip Thrust)" },
    { text: "Dominadas", value: "Jalones y Dominadas" },
    { text: "Laterales", value: "Elevaciones Laterales" },
    { text: "Remo", value: "Remos (Rows)" }
];

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function stopCurrentTyping() {
    if (activeTypewriterId) {
        clearTimeout(activeTypewriterId);
        activeTypewriterId = null;
    }
}

function clearShortcuts() {
    const existing = document.querySelectorAll('.shortcuts-inline');
    existing.forEach(el => el.remove());
}

function renderButtons(tipo) {
    clearShortcuts();
    const container = document.createElement('div');
    container.className = 'shortcuts-inline';
    
    let items = [];

    if (tipo === 'inicio') {
        items = [
            { display: 'Explicar músculo', func: 'explicar musculo', val: null, next: 'musculos' },
            { display: 'Explicar ejercicio', func: 'explicar ejercicio', val: null, next: 'ejercicios' },
            { display: 'Info', func: 'info', val:[] , next: null }
        ];
    } 
    else if (tipo === 'musculos') {
        items.push({ display: '← Volver', isBack: true, action: () => renderButtons('inicio') });
        listaMusculos.forEach(m => {
            items.push({ display: m.text, func: 'explicar musculo', val: [m.value] });
        });
    } 
    else if (tipo === 'ejercicios') {
        items.push({ display: '← Volver', isBack: true, action: () => renderButtons('inicio') });
        listaEjercicios.forEach(e => {
            items.push({ display: e.text, func: 'explicar ejercicio', val: [e.value] });
        });
    }

    items.forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'btn-chip';
        
        if (item.isBack) {
            btn.style.background = '#333';
            btn.style.color = 'var(--primary)';
            btn.onclick = item.action;
        } else if (item.next) {
            // Si es un botón que abre otra lista (ej: "Explicar músculo")
            btn.onclick = () => renderButtons(item.next);
        } else {
            // Si es un botón final (ej: "Banca")
            btn.onclick = () => sendDirect(item.func, item.val, item.display);
        }
        
        btn.textContent = item.display;
        container.appendChild(btn);
    });

    chatWindow.appendChild(container);
    scrollToBottom();
}

/**
 * @param {string} func - Nombre de la función en Python
 * @param {string} arg - El nombre LARGO para Python
 * @param {string} display - El nombre CORTO para mostrar en el chat
 */
function sendDirect(func, arg, display) {
    clearShortcuts();
    // En el chat mostramos el nombre corto para que quede limpio
    appendMessage(display, 'user');
    
    // Al servidor enviamos el argumento real (el largo)
    socket.emit('direct_message', { 
        funcion: func,
        argumento: arg 
    });
}

// ... (Resto de funciones typeWriter, appendMessage y eventListeners iguales) ...

function typeWriter(element, text, isError) {
    let i = 0;
    const speed = 15;
    function type() {
        if (i < text.length) {
            element.innerHTML = marked.parse(text.substring(0, i + 1));
            i++;
            scrollToBottom();
            activeTypewriterId = setTimeout(type, speed);
        } else {
            activeTypewriterId = null;
            if (isError) setTimeout(() => renderButtons('inicio'), 300);
        }
    }
    type();
}

function appendMessage(text, sender) {
    if (sender === 'user') {
        stopCurrentTyping();
        clearShortcuts();
    }
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
        const frasesError = ["no estoy seguro de haberte entendido", "pregúntame cosas como", "inténtalo de nuevo"];
        const esError = frasesError.some(frase => text.toLowerCase().includes(frase));
        typeWriter(bubble, text, esError);
    } else {
        bubble.textContent = text;
        msgDiv.appendChild(bubble);
        chatWindow.appendChild(msgDiv);
    }
    scrollToBottom();
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = inputMessage.value.trim();
    if (msg) {
        appendMessage(msg, 'user');
        socket.emit('message', msg);
        inputMessage.value = '';
    }
});

socket.on('message', (msg) => appendMessage(msg, 'bot'));

window.onload = () => {
    setTimeout(() => renderButtons('inicio'), 1500);
};