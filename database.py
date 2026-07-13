import sqlite3
from datetime import datetime


DATABASE_NAME = "pourya_trader.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        role TEXT DEFAULT 'USER',
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT
    )
    """)

    # Exchange accounts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exchange TEXT,
        api_key TEXT,
        api_secret TEXT,
        capital REAL DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Trades table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT,
        side TEXT,
        entry REAL,
        exit REAL,
        profit REAL DEFAULT 0,
        status TEXT DEFAULT 'OPEN',
        opened_at TEXT,
        closed_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Profit sharing table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profit_share (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        profit REAL,
        fee_percent REAL,
        fee_amount REAL,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


def add_user(telegram_id, name, role="USER"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (telegram_id, name, role, created_at)
    VALUES (?, ?, ?, ?)
    """,
    (
        telegram_id,
        name,
        role,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users
    WHERE telegram_id=?
    """,
    (telegram_id,))

    user = cursor.fetchone()

    conn.close()

    return user
