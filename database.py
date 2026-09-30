import sqlite3
from datetime import datetime

DB_PATH = "chat_history.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            sources TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_message(question, answer, sources):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO chat_history (question, answer, sources, created_at) VALUES (?, ?, ?, ?)",
        (question, answer, str(sources), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]