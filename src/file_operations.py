import json
import os
import glob

def get_all_chats():
    """Возвращает список ID всех существующих чатов (имена файлов без .json)."""
    files = glob.glob('storage/chat_*.json')
    # Вырезаем 'storage/chat_' и '.json', чтобы остался только ID
    return [os.path.basename(f).replace('chat_', '').replace('.json', '') for f in files]

def read_json(file_path):
    """
    Универсальное чтение JSON. 
    Если файла нет или он битый — возвращаем пустой список.
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Если файл пустой или там не JSON — возвращаем пустой список
        return []
    
def write_json(file_path, data):
    """
    Универсальная запись в JSON.
    Создает папку, если её нет.
    """
    # На всякий случай проверяем/создаем папку (например, storage/)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        print(f"Ошибка записи в файл {file_path}: {e}")
        return False
    
def append_to_history(file_path, role, content):
    """
    Специализированная функция для добавления сообщения в историю.
    """
    history = read_json(file_path)
    history.append({"role": role, "content": content})
    write_json(file_path, history)

def delete_json_file(file_path):
    """Удаляет файл, если он существует."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except OSError as e:
        print(f"Ошибка при удалении файла {file_path}: {e}")
        return False