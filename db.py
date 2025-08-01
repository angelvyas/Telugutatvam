# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            swecha_username TEXT,
            location TEXT,
            category TEXT,
            prompt TEXT,
            mode TEXT,
            text_response TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_response(data):
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO responses (name, email, swecha_username, location, category, prompt, mode, text_response, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["email"],
        data["swecha_username"],
        data["location"],
        data["category"],
        data["prompt"],
        data["mode"],
        data.get("text_response", ""),  # fallback to empty string if not present
        data["timestamp"]
    ))
    conn.commit()
    conn.close()

