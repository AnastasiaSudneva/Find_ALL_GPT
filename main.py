import logging
import sqlite3

import telebot
from config import BOT_TOKEN
from db import initialize_db
from gpt_integration import get_gpt_response
from message_handler import welcome_message

# Инициализация бота с использованием токена из файла конфигурации
bot = telebot.TeleBot(BOT_TOKEN)


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
    Отправляет приветственное сообщение и клавиатуру с командами при старте бота.

    :param message: Объект сообщения от пользователя.
    """
    bot.reply_to(message, welcome_message,
                 reply_markup=generate_reply_markup())


def generate_markup():
    """
    Создает inline-клавиатуру с кнопками для дополнительных действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    switch_button = telebot.types.InlineKeyboardButton(text="Ответь по-другому", callback_data="switch")
    good_response_button = telebot.types.InlineKeyboardButton(text="Хороший ответ✅", callback_data="good_response")
    markup.add(switch_button, good_response_button)
    return markup


def generate_reply_markup():
    """
    Создает клавиатуру с кнопками для основных команд.

    :return: Объект ReplyKeyboardMarkup для отправки пользователю.
    """
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    clear_history_button = telebot.types.KeyboardButton('Очистить историю🗑️')
    about_button = telebot.types.KeyboardButton('Расскажи о себе💬')
    markup.add(clear_history_button, about_button)
    return markup


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Обрабатывает текстовые сообщения, отправленные пользователем.

    :param message: Объект сообщения от пользователя.
    """
    bot.send_chat_action(message.chat.id, 'typing')

    # Проверяем, содержит ли сообщение команду "Очистить историю"
    if message.text == "Очистить историю🗑️":
        try:
            # Вызываем функцию для очистки истории сообщений
            clear_history(message.chat.id)
            bot.send_message(message.chat.id, "Ваша история сообщений была очищена.")
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз!")
    else:
        # Если сообщение не является командой, отправляем его в GPT
        try:
            response = get_gpt_response(message.text)
            save_message(message.chat.id, message.message_id, message.text, response)
            bot.send_message(message.chat.id, response, reply_markup=generate_markup())
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз!")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    """
    Обрабатывает нажатия на inline-кнопки.

    :param call: Объект callback-запроса от inline-кнопки.
    """
    message = call.message
    bot.answer_callback_query(callback_query_id=call.id)

    if call.data == "switch":
        try:
            # Получаем последнее сообщение пользователя
            last_message = get_last_message(message.chat.id)
            if last_message:
                response = get_gpt_response(last_message, switch=True)
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=response,
                                      reply_markup=generate_markup())
            else:
                bot.send_message(message.chat.id, "Извините, я не смог найти ваш последний запрос.")
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз!")
    elif call.data == "good_response":
        try:
            # Сохранение положительного отзыва
            save_feedback(message.chat.id, message.message_id, "good")
            bot.send_message(message.chat.id, "Спасибо за ваш положительный отзыв!")
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз!")


@bot.message_handler(func=lambda message: message.text == "Очистить историю")
def handle_clear_history(message):
    """
    Обрабатывает команду 'Очистить историю', удаляя историю сообщений пользователя из базы данных.

    :param message: Объект сообщения от пользователя.
    """
    try:
        clear_history(message.chat.id)
        bot.send_message(message.chat.id, "Ваша история сообщений была очищена.")
        logger.info(f"История сообщений для {message.chat.id} очищена.")
    except Exception as e:
        logger.error(f"Ошибка при очистке истории для {message.chat.id}: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка!")


def clear_history(chat_id):
    """
    Удаляет всю историю сообщений и обратную связь для заданного chat_id из базы данных.

    :param chat_id: ID чата пользователя для удаления истории.
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    c.execute("DELETE FROM feedback WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"История для пользователя {chat_id} очищена.")


def save_message(chat_id, message_id, text, response=""):
    """
    Сохраняет сообщение и ответ на него в базу данных.

    :param chat_id: ID чата пользователя.
    :param message_id: ID сообщения.
    :param text: Текст сообщения пользователя.
    :param response: Текст ответа бота.
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (chat_id, message_id, text, response) VALUES (?, ?, ?, ?)",
              (chat_id, message_id, text, response))
    conn.commit()
    conn.close()
    logger.info(f"Сообщение от пользователя {chat_id} сохранено в базе данных.")


def get_last_message(chat_id):
    """
    Извлекает последнее сообщение пользователя из базы данных.

    :param chat_id: ID чата пользователя.
    :return: Текст последнего сообщения пользователя.
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT text FROM messages WHERE chat_id=? ORDER BY message_id DESC LIMIT 1", (chat_id,))
    last_message = c.fetchone()
    conn.close()
    return last_message[0] if last_message else None


def save_feedback(chat_id, message_id, feedback):
    """
    Сохраняет обратную связь пользователя в базу данных.

    :param chat_id: ID чата пользователя.
    :param message_id: ID сообщения.
    :param feedback: Текст обратной связи.
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (chat_id, message_id, feedback) VALUES (?, ?, ?)",
              (chat_id, message_id, feedback))
    conn.commit()
    conn.close()
    logger.info(f"Обратная связь от пользователя {chat_id} сохранена в базе данных.")


# Запуск бота
if __name__ == '__main__':
    initialize_db()
    logger.info("Бот запущен.")
    bot.infinity_polling()
