import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "chat.db")


def get_connection():
    # 🔹 ADDED: row_factory for cleaner dict-style access (optional but useful)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 USERS TABLE (unchanged, correct)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # 🔹 MESSAGES TABLE (minor refinements)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized at:", DB_PATH)


def get_last_messages(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, content, timestamp
        FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    # 🔹 CHANGED: return JSON-ready dicts, not raw tuples
    return [
        {
            "username": row["username"],
            "content": row["content"],
            "timestamp": row["timestamp"]
        }
        for row in reversed(rows)
    ]
