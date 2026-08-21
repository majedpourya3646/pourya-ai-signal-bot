import sqlite3
import os

from core.logger import logger


# ===========================
# Database
# ===========================

DB_PATH = "data/pourya_trader.db"


# ===========================
# Ensure Directory
# ===========================

def ensure_directory():

    try:

        folder = os.path.dirname(
            DB_PATH
        )

        if folder and not os.path.exists(
            folder
        ):

            os.makedirs(
                folder
            )

    except Exception as e:

        logger.exception(
            f"DATABASE DIRECTORY ERROR {e}"
        )


# ===========================
# Connection
# ===========================

def get_connection():

    try:

        ensure_directory()

        conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        conn.row_factory = sqlite3.Row

        return conn

    except Exception as e:

        logger.exception(
            f"DATABASE CONNECTION ERROR {e}"
        )

        return None


# ===========================
# Initialize Database
# ===========================

def initialize_database():

    try:

        conn = get_connection()

        if conn is None:

            return False

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

        conn.close()

        logger.info(
            "DATABASE INITIALIZED"
        )

        return True

    except Exception as e:

        logger.exception(
            f"DATABASE INITIALIZATION ERROR {e}"
        )

        return False


# ===========================
# Database Status
# ===========================

def database_status():

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

    except Exception as e:

        logger.exception(
            f"DATABASE STATUS ERROR {e}"
        )

        return False


# ===========================
# Reset Database
# ===========================

def reset_database():

    try:

        if os.path.exists(
            DB_PATH
        ):

            os.remove(
                DB_PATH
            )

        logger.warning(
            "DATABASE RESET"
        )

        return initialize_database()

    except Exception as e:

        logger.exception(
            f"DATABASE RESET ERROR {e}"
        )

        return False
