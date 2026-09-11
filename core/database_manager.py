# core/database_manager.py

from __future__ import annotations

import os
import sqlite3

from core.logger import logger


# ===========================
# Database Configuration
# ===========================

DB_PATH = "data/pourya_trader.db"


# ===========================
# Ensure Directory
# ===========================

def ensure_directory() -> bool:
    try:
        folder = os.path.dirname(DB_PATH)

        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        return True

    except Exception as exc:
        logger.exception(
            f"DATABASE DIRECTORY ERROR {exc}"
        )
        return False


# ===========================
# Create Tables
# ===========================

def _create_tables(conn: sqlite3.Connection) -> bool:
    try:
        cursor = conn.cursor()

        # ===========================
        # Trades
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                ticket INTEGER,

                symbol TEXT,

                side TEXT,

                entry REAL,

                exit_price REAL,

                tp REAL,

                sl REAL,

                quantity REAL,

                confidence REAL,

                pnl REAL DEFAULT 0,

                status TEXT,

                opened_at TEXT,

                closed_at TEXT
            )
            """
        )

        # ===========================
        # Users
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                username TEXT,

                trading_mode TEXT,

                profit_percent REAL,

                active INTEGER,

                created_at TEXT
            )
            """
        )

        # ===========================
        # Subscriptions
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                plan TEXT,

                start_date TEXT,

                expire_date TEXT,

                active INTEGER
            )
            """
        )

        # ===========================
        # Payments
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                amount REAL,

                currency TEXT,

                status TEXT,

                description TEXT,

                created_at TEXT
            )
            """
        )

        # ===========================
        # Profits
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profits
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                trade_id INTEGER,

                gross_profit REAL,

                user_profit REAL,

                system_profit REAL,

                created_at TEXT
            )
            """
        )

        conn.commit()

        return True

    except Exception as exc:
        logger.exception(
            f"DATABASE TABLE CREATION ERROR {exc}"
        )
        return False


# ===========================
# Connection
# ===========================

def get_connection():
    try:
        if not ensure_directory():
            return None

        conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        conn.row_factory = sqlite3.Row

        # Always make sure required tables exist.
        if not _create_tables(conn):
            conn.close()
            return None

        return conn

    except Exception as exc:
        logger.exception(
            f"DATABASE CONNECTION ERROR {exc}"
        )
        return None


# ===========================
# Initialize Database
# ===========================

def initialize_database() -> bool:
    try:
        conn = get_connection()

        if conn is None:
            logger.error(
                "DATABASE INITIALIZATION FAILED"
            )
            return False

        conn.close()

        logger.info(
            "DATABASE INITIALIZED"
        )

        return True

    except Exception as exc:
        logger.exception(
            f"DATABASE INITIALIZATION ERROR {exc}"
        )
        return False


# ===========================
# Database Status
# ===========================

def database_status() -> bool:
    try:
        conn = get_connection()

        if conn is None:
            return False

        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1"
        )

        result = cursor.fetchone()

        conn.close()

        return result is not None

    except Exception as exc:
        logger.exception(
            f"DATABASE STATUS ERROR {exc}"
        )
        return False


# ===========================
# Reset Database
# ===========================

def reset_database() -> bool:
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        logger.warning(
            "DATABASE RESET"
        )

        return initialize_database()

    except Exception as exc:
        logger.exception(
            f"DATABASE RESET ERROR {exc}"
        )
        return False


__all__ = [
    "DB_PATH",
    "ensure_directory",
    "get_connection",
    "initialize_database",
    "database_status",
    "reset_database",
]
