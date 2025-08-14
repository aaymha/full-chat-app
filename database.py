import asyncio
import sqlite3

async def init_database():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            username TEXT,
            message TEXT,
            timestamp TIMESTAMP
        )
    ''')
    conn.close()

async def save_message(username, user_message):
    conn = sqlite3.connect('messages.db')
    curs = conn.cursor()

    curs.execute("INSERT INTO messages (username, message) VALUES (?, ?)",
                 (username, user_message,))
    conn.commit()
    conn.close()


def recent_messages():  # Remove async
    conn = sqlite3.connect('messages.db')
    curs = conn.cursor()

    curs.execute("SELECT messages.message from messages")
    messages = curs.fetchall()

    return [msg[0].strip() for msg in messages]












