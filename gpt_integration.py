import g4f

from message_handler import prompt_for_gpt


def get_gpt_response(message, switch=False):
    try:
        prompt = prompt_for_gpt + message
        if switch:
            prompt += "\nПожалуйста, дайте другой ответ на этот же вопрос."

        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            timeout=120,  # in secs
        )
        return response
    except Exception as e:
        return f"Ошибка: {e}"
