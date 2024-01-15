import g4f  # Импорт модуля 'g4f'

from message_handler import prompt_for_gpt  # Импорт 'prompt_for_gpt' из модуля 'message_handler'


def get_gpt_response(message,
                     switch=False):  # Определение функции 'get_gpt_response' с параметрами 'message' и 'switch' (по умолчанию False).
    try:  # Начало блока try для перехвата исключений, которые могут возникнуть внутри блока.
        prompt = prompt_for_gpt + message  # Конкатенация 'prompt_for_gpt' с аргументом 'message' для формирования полной подсказки для GPT. Здесь мы указываем боту его область и сам запрос пользователя
        if switch:  # Проверка, равен ли аргумент 'switch' значению True.
            prompt += "\nПожалуйста, дайте другой ответ на этот же вопрос."  # Если 'switch' равен True, добавляется предложение с просьбой дать другой ответ на тот же вопрос. Когда нажимаем кнопку другой ответ

        response = g4f.ChatCompletion.create(  # Создание запроса к gpt.
            model=g4f.models.default,  # Указание на использование стандартной модели из 'g4f.models'.
            messages=[{"role": "user", "content": prompt}],
            # Выбираем модель юзер, в content передается содержание запроса
            timeout=120,  # Установка времени ожидания ответа от GPT в 120 секунд.
        )
        return response  # Возврат полученного от GPT ответа.

    except Exception as e:  # Перехват любых исключений, возникших в блоке try.
        return f"Ошибка: {e}"  # Возврат сообщения об ошибке с деталями исключения.
