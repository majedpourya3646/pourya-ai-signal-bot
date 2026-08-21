import os
import sqlite3

from core.logger import logger


# ===========================
# Database Configuration
# ===========================

DATABASE_DIR = "data"
DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "trades.db"
)


# ===========================
# Connection
# ===========================

def get_connection():

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ===========================
# Initialize Database
# ===========================

def initialize_database():

    try:

        os.makedirs(
            DATABASE_DIR,
            exist_ok=True
        )


        connection = get_connection()

        cursor = connection.cursor()


        # ===========================
        # Trades
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT NOT NULL,

                side TEXT NOT NULL,

                order_type TEXT DEFAULT 'market',

                volume REAL DEFAULT 0,

                entry_price REAL DEFAULT 0,

                take_profit REAL DEFAULT 0,

                stop_loss REAL DEFAULT 0,

                leverage REAL DEFAULT 1,

                status TEXT DEFAULT 'OPEN',

                profit REAL DEFAULT 0,

                commission REAL DEFAULT 0,

                ticket TEXT,

                broker TEXT DEFAULT 'MT5',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                closed_at TEXT,

                notes TEXT

            )
            """
        )


        # ===========================
        # System State
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS system_state (

                key TEXT PRIMARY KEY,

                value TEXT,

                updated_at TEXT DEFAULT CURRENT_TIMESTAMP

            )
            """
        )


        # ===========================
        # Users
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                username TEXT,

                profit_share REAL DEFAULT 70,

                balance REAL DEFAULT 0,

                total_profit REAL DEFAULT 0,

                total_loss REAL DEFAULT 0,

                active INTEGER DEFAULT 1,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP

            )
            """
        )


        # ===========================
        # Trade Events
        # ===========================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trade_events (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                trade_id INTEGER,

                event_type TEXT,

                message TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (trade_id)
                    REFERENCES trades(id)

            )
            """
        )


        connection.commit()

        connection.close()


        logger.info(
            "DATABASE INITIALIZED"
        )


        return True


    except Exception as exc:

        logger.exception(
            "DATABASE INITIALIZATION FAILED: %s",
            exc
        )

        return False


# ===========================
# Trade Insert
# ===========================

def create_trade(
    symbol,
    side,
    volume,
    entry_price,
    take_profit=0,
    stop_loss=0,
    leverage=1,
    ticket=None,
    status="OPEN",
    notes=None
):

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO trades (

                symbol,
                side,
                order_type,
                volume,
                entry_price,
                take_profit,
                stop_loss,
                leverage,
                status,
                ticket,
                broker,
                notes

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol,
                side,
                "market",
                volume,
                entry_price,
                take_profit,
                stop_loss,
                leverage,
                status,
                str(ticket) if ticket is not None else None,
                "MT5",
                notes
            )
        )


        trade_id = cursor.lastrowid

        connection.commit()


        return trade_id


    except Exception as exc:

        logger.exception(
            "CREATE TRADE FAILED: %s",
            exc
        )

        return None


    finally:

        if connection:

            connection.close()


# ===========================
# Get Open Trades
# ===========================

def get_open_trades():

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT *

            FROM trades

            WHERE status = 'OPEN'

            ORDER BY id DESC
            """
        )


        rows = cursor.fetchall()


        return [
            dict(row)
            for row in rows
        ]


    except Exception as exc:

        logger.exception(
            "GET OPEN TRADES FAILED: %s",
            exc
        )

        return []


    finally:

        if connection:

            connection.close()


# ===========================
# Update Trade
# ===========================

def update_trade(
    trade_id,
    **fields
):

    if not fields:

        return False


    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        allowed_fields = {

            "status",
            "profit",
            "commission",
            "closed_at",
            "entry_price",
            "take_profit",
            "stop_loss",
            "ticket",
            "notes"

        }


        updates = []

        values = []


        for key, value in fields.items():

            if key not in allowed_fields:

                continue


            updates.append(
                f"{key} = ?"
            )

            values.append(
                value
            )


        if not updates:

            return False


        values.append(
            trade_id
        )


        query = f"""
            UPDATE trades

            SET {", ".join(updates)}

            WHERE id = ?
        """


        cursor.execute(
            query,
            values
        )


        connection.commit()


        return cursor.rowcount > 0


    except Exception as exc:

        logger.exception(
            "UPDATE TRADE FAILED: %s",
            exc
        )

        return False


    finally:

        if connection:

            connection.close()


# ===========================
# Get Trade
# ===========================

def get_trade(
    trade_id
):

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT *

            FROM trades

            WHERE id = ?

            LIMIT 1
            """,
            (
                trade_id,
            )
        )


        row = cursor.fetchone()


        if row is None:

            return None


        return dict(row)


    except Exception as exc:

        logger.exception(
            "GET TRADE FAILED: %s",
            exc
        )

        return None


    finally:

        if connection:

            connection.close()


# ===========================
# System State
# ===========================

def set_system_state(
    key,
    value
):

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO system_state (
                key,
                value,
                updated_at
            )

            VALUES (?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(key)

            DO UPDATE SET

                value = excluded.value,

                updated_at = CURRENT_TIMESTAMP
            """,
            (
                key,
                str(value)
            )
        )


        connection.commit()


        return True


    except Exception as exc:

        logger.exception(
            "SET SYSTEM STATE FAILED: %s",
            exc
        )

        return False


    finally:

        if connection:

            connection.close()


def get_system_state(
    key,
    default=None
):

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT value

            FROM system_state

            WHERE key = ?

            LIMIT 1
            """,
            (
                key,
            )
        )


        row = cursor.fetchone()


        if row is None:

            return default


        return row["value"]


    except Exception as exc:

        logger.exception(
            "GET SYSTEM STATE FAILED: %s",
            exc
        )

        return default


    finally:

        if connection:

            connection.close()
