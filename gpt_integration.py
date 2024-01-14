import g4f


def get_gpt_response(message, switch=False):
    try:
        prompt = message
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
