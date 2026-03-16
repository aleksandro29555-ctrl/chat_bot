from flask import Flask, render_template, request, jsonify
from src.conditions import get_bot_response  # Импортируем нашу логику
from src.functions import process_mathematics  # Импортируем функцию для обработки математики
from src.file_operations import read_json, append_to_history, get_all_chats, delete_json_file  # Импортируем функции для работы с историей
import uuid

app = Flask(__name__)

HISTORY_PATH = 'storage/chat_history.json'

@app.route('/get_chats', methods=['GET'])
def list_chats():
    # Возвращаем список ID всех чатов из папки storage
    chats = get_all_chats() 
    return jsonify(chats)

@app.route('/get_history', methods=['GET'])
def get_history():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return jsonify([])
    
    file_path = f'storage/chat_{chat_id}.json'
    return jsonify(read_json(file_path))

@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    data = request.json
    chat_id = data.get('chat_id')
    
    if not chat_id:
        return jsonify({"status": "error", "message": "ID не предоставлен"}), 400

    file_path = f'storage/chat_{chat_id}.json'
    
    # Пытаемся удалить через наш модуль
    if delete_json_file(file_path):
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Файл не найден или ошибка доступа"}), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_message = data.get('message', '')
    chat_id = data.get('chat_id')

    if not chat_id:
        chat_id = str(uuid.uuid4())[:8]  # Генерируем короткий ID для нового чата
    
    bot_reply = get_bot_response(user_message)
    # Вызываем логику из conditions.py
    if bot_reply is None:
        bot_reply = process_mathematics(user_message)

    if bot_reply is None:
        bot_reply = "Извини, я пока не знаю, как на это ответить."
    
    chat_path = f'storage/chat_{chat_id}.json'
    # Сохраняем в историю
    append_to_history(chat_path, "user", user_message)
    append_to_history(chat_path, "bot", bot_reply)
    
    return jsonify({'reply': bot_reply, 'chat_id': chat_id})

if __name__ == '__main__':
    app.run(debug=True)