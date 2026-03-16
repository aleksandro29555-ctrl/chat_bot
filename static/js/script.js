let currentChatId = null;
const historyContainer = document.getElementById('messages-history');
const userInput = document.getElementById('user-input');

async function greetUser() {
    const response = await fetch('/get_user_info');
    const settings = await response.json();
    
    // Если мы в новом чате и там еще нет сообщений - выводим приветствие
    if (historyContainer.children.length === 0) {
        appendMessage('bot', `Привет, ${settings.user_name}! Чем могу помочь сегодня?`);
    }
}

function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    const name = sender === 'user' ? 'Вы' : (sender === 'bot' ? 'Бот' : sender);
    messageDiv.innerHTML = `<strong>${name}:</strong> ${text}`;
    historyContainer.appendChild(messageDiv);
    historyContainer.scrollTop = historyContainer.scrollHeight;
}

async function loadChatList() {
    const response = await fetch('/get_chats');
    const chats = await response.json();
    const chatListContainer = document.querySelector('.chat-list');
    
    chatListContainer.innerHTML = '<div class="chat-item" id="new-chat-btn" style="background: #10a37f; justify-content: center;">+ Новый чат</div>';
    document.getElementById('new-chat-btn').onclick = createNewChat;

    chats.forEach(id => {
        const div = document.createElement('div');
        div.className = 'chat-item';
        
        // Текст чата
        const span = document.createElement('span');
        span.innerText = `Чат ${id}`;
        span.onclick = () => loadChat(id);
        
        // Кнопка удаления
        const delBtn = document.createElement('span');
        delBtn.className = 'delete-btn';
        delBtn.innerHTML = '&times;'; // Символ крестика
        delBtn.onclick = (e) => {
            e.stopPropagation(); // Чтобы не сработал клик по самому чату
            deleteChat(id);
        };

        div.appendChild(span);
        div.appendChild(delBtn);
        chatListContainer.appendChild(div);
    });
}

async function deleteChat(id) {
    if (!confirm(`Удалить чат ${id}?`)) return;

    const response = await fetch('/delete_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: id })
    });

    const data = await response.json();
    if (data.status === 'success') {
        // Если удалили тот чат, в котором сейчас находимся — сбрасываем экран
        if (currentChatId === id) {
            startNewChat();
        }
        loadChatList(); // Перерисовываем список
    } else {
        alert("Не удалось удалить чат");
    }
}

async function loadChat(id) {
    console.log("Загружаем чат с ID:", id); // Для отладки в консоли браузера
    currentChatId = id;
    
    try {
        const response = await fetch(`/get_history?chat_id=${id}`);
        const history = await response.json();
        
        console.log("Полученные данные:", history); // Посмотри, что пришло

        const historyContainer = document.getElementById('messages-history');
        historyContainer.innerHTML = ''; // Обязательно чистим контейнер
        
        if (history.length === 0) {
            historyContainer.innerHTML = '<div class="message">История пуста</div>';
        } else {
            history.forEach(msg => {
                // Убедись, что ключи в JSON называются так же: role и content
                appendMessage(msg.role, msg.content);
            });
        }
    } catch (error) {
        console.error("Ошибка при загрузке истории:", error);
    }
}

function createNewChat() {
    currentChatId = null; // Сбрасываем ID
    document.getElementById('messages-history').innerHTML = ''; // Очищаем экран
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('input-area');
    const input = document.getElementById('user-input');
    const history = document.getElementById('messages-history');

    loadChatList();

    (async () => {
        try {
            const response = await fetch('/get_user_info');
            const settings = await response.json();
            
            // Здороваемся только если чат пустой (новый)
            if (history.children.length === 0) {
                appendMessage('Бот', `Привет, ${settings.user_name}! Чем могу помочь?`);
            }
        } catch (e) {
            console.error("Не удалось получить настройки пользователя");
        }
    })();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();

        if (text !== "") {
            // 1. Отображаем сообщение пользователя
            appendMessage('Вы', text);
            input.value = "";

            // 2. Отправляем запрос на сервер
            try {
                const response = await fetch('/get_response', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message: text, 
                        chat_id: currentChatId // Отправляем текущий ID
                    })
                });

                const data = await response.json();
                if (!currentChatId) {
                    currentChatId = data.chat_id; // Запоминаем ID, который прислал сервер
                    loadChatList(); // Обновляем список слева
                }
                // 3. Отображаем ответ бота
                appendMessage('Бот', data.reply);
            } catch (error) {
                console.error('Ошибка:', error);
                appendMessage('Система', 'Ошибка связи с сервером.');
            }
        }
    });
});