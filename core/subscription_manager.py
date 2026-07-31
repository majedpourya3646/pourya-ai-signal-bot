# core/subscription_manager.py

import sqlite3

from datetime import datetime, timedelta

from core.logger import logger

DB_PATH = "data/pourya_trader.db"


def get_connection():

    try:

        return sqlite3.connect(DB_PATH)

    except Exception as e:

        logger.exception(e)

        return None


def init_subscription_database():

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE,
                plan TEXT,
                start_date TEXT,
                expire_date TEXT,
                active INTEGER DEFAULT 1
            )
            """
        )

        conn.commit()
        conn.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def create_subscription(
    telegram_id,
    plan="FREE",
    days=30
):

    try:

        conn = get_connection()

        cursor = conn.cursor()

        start = datetime.utcnow()

        expire = start + timedelta(days=days)

        cursor.execute(
            """
            INSERT OR REPLACE INTO subscriptions
            (
                telegram_id,
                plan,
                start_date,
                expire_date,
                active
            )
            VALUES (?,?,?,?,?)
            """,
            (
                str(telegram_id),
                plan,
                start.isoformat(),
                expire.isoformat(),
                1
            )
        )

        conn.commit()
        conn.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def get_subscription(telegram_id):

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                plan,
                start_date,
                expire_date,
                active
            FROM subscriptions
            WHERE telegram_id=?
            """,
            (str(telegram_id),)
        )

        row = cursor.fetchone()

        conn.close()

        if not row:

            return None

        return {
            "plan": row[0],
            "start_date": row[1],
            "expire_date": row[2],
            "active": bool(row[3])
        }

    except Exception as e:

        logger.exception(e)

        return None


def check_subscription(telegram_id):

    try:

        sub = get_subscription(telegram_id)

        if not sub:

            return False

        if not sub["active"]:

            return False

        expire = datetime.fromisoformat(
            sub["expire_date"]
        )

        return expire > datetime.utcnow()

    except Exception as e:

        logger.exception(e)

        return False


def extend_subscription(
    telegram_id,
    days
):

    try:

        sub = get_subscription(
            telegram_id
        )

        if not sub:

            return False

        expire = datetime.fromisoformat(
            sub["expire_date"]
        )

        if expire < datetime.utcnow():

            expire = datetime.utcnow()

        expire += timedelta(days=days)

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE subscriptions
            SET expire_date=?
            WHERE telegram_id=?
            """,
            (
                expire.isoformat(),
                str(telegram_id)
            )
        )

        conn.commit()
        conn.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def deactivate_subscription(
    telegram_id
):

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE subscriptions
            SET active=0
            WHERE telegram_id=?
            """,
            (str(telegram_id),)
        )

        conn.commit()
        conn.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def get_active_subscribers():

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT telegram_id
            FROM subscriptions
            WHERE active=1
            """
        )

        rows = cursor.fetchall()

        conn.close()

        return [r[0] for r in rows]

    except Exception as e:

        logger.exception(e)

        return []
