import math
import re

def process_mathematics(user_message):
    # Нормализуем строку для поиска
    text = user_message.lower().strip().replace(',', '.')

    # Регулярное выражение для поиска чисел (целые и десятичные)
    num_pattern = r'-?\d+\.?\d*'

    # 1. Обработка Квадратного корня (sqrt 16 или √16)
    # Ищем слово sqrt или символ √, а затем число
    sqrt_match = re.search(r'(sqrt|√)\s*(' + num_pattern + ')', text)
    if sqrt_match:
        try:
            number = float(sqrt_match.group(2))
            if number < 0:
                return "Математическая ошибка: нельзя извлечь корень из отрицательного числа."
            result = math.sqrt(number)
            res_str = int(result) if result.is_integer() else round(result, 4)
            return f"Результат: {res_str}"
        except Exception:
            return "Ошибка при вычислении корня."

    # 2. Бинарные операции (2+2, 5-3, 4*7, 8/2, 2^3)
    # Регулярка ищет: число [пробелы] знак [пробелы] число
    # Поддерживаем знаки: +, -, *, /, ^, **
    binary_match = re.search(r'(' + num_pattern + r')\s*(\*\*|[\+\-\*/\^])\s*(' + num_pattern + ')', text)
    if binary_match:
        try:
            val1 = float(binary_match.group(1))
            op = binary_match.group(2)
            val2 = float(binary_match.group(3))

            if op == '+': result = val1 + val2
            elif op == '-': result = val1 - val2
            elif op == '*': result = val1 * val2
            elif op == '/' :
                if val2 == 0: return "На ноль делить нельзя!"
                result = val1 / val2
            elif op == '^' or op == '**': 
                result = val1 ** val2
            
            res_str = int(result) if result.is_integer() else round(result, 4)
            return f"Результат: {res_str}"
        except Exception:
            return "Ошибка в вычислениях."
        
    # Если ничего не подошло, возвращаем None, чтобы main пошел проверять другие блоки
    return None