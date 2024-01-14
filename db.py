import sqlite3


def initialize_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()

    # Создание таблицы для сообщений, если она еще не существует
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (chat_id INTEGER, message_id INTEGER, text TEXT, response TEXT)''')

    # Создание таблицы для отзывов, если она еще не существует
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (chat_id INTEGER, message_id INTEGER, feedback TEXT)''')

    conn.commit()
    conn.close()

