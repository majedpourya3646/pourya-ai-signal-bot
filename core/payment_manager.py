# core/payment_manager.py

from datetime import datetime
from core.database_manager import get_connection
from core.logger import logger

PAYMENT_STATUS = (
    "PENDING",
    "SUCCESS",
    "FAILED",
    "CANCELLED"
)


def init_payment_database():

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                transaction_id TEXT,
                status TEXT NOT NULL,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        conn.commit()
        conn.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def create_payment(
    telegram_id,
    amount,
    currency="USDT",
    payment_method="CRYPTO",
    description=""
):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute(
            """
            INSERT INTO payments
            (
                telegram_id,
                amount,
                currency,
                payment_method,
                status,
                description,
                created_at,
                updated_at
            )
            VALUES
            (
                ?,?,?,?,?,?,?,?
            )
            """,
            (
                str(telegram_id),
                float(amount),
                currency,
                payment_method,
                "PENDING",
                description,
                now,
                now
            )
        )

        payment_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return payment_id

    except Exception as e:

        logger.exception(e)

        return None


def update_payment_status(
    payment_id,
    status,
    transaction_id=None
):

    try:

        if status not in PAYMENT_STATUS:

            return False

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE payments
            SET
                status=?,
                transaction_id=?,
                updated_at=?
            WHERE id=?
            """,
            (
                status,
                transaction_id,
                datetime.utcnow().isoformat(),
                payment_id
            )
        )

        conn.commit()
        conn.close()

        return True

    except Exception as e:

        logger.exception(e)

        return False


def get_payment(payment_id):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM payments
            WHERE id=?
            """,
            (payment_id,)
        )

        row = cursor.fetchone()

        conn.close()

        return row

    except Exception as e:

        logger.exception(e)

        return None


def get_user_payments(
    telegram_id
):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM payments
            WHERE telegram_id=?
            ORDER BY id DESC
            """,
            (str(telegram_id),)
        )

        rows = cursor.fetchall()

        conn.close()

        return rows

    except Exception as e:

        logger.exception(e)

        return []


def successful_payments_total():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT SUM(amount)
            FROM payments
            WHERE status='SUCCESS'
            """
        )

        result = cursor.fetchone()

        conn.close()

        if result and result[0]:

            return float(result[0])

        return 0.0

    except Exception as e:

        logger.exception(e)

        return 0.0


def payment_statistics():

    return {

        "total_income":
            successful_payments_total(),

        "generated_at":
            datetime.utcnow().isoformat()

    }
