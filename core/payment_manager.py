# core/payment_manager.py

import sqlite3

from datetime import datetime

from core.logger import logger





DB_PATH = "data/pourya_trader.db"








def get_connection():

    try:

        return sqlite3.connect(

            DB_PATH

        )


    except Exception as e:


        logger.exception(e)


        return None








def init_payment_database():

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS payments

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                amount REAL,

                currency TEXT DEFAULT 'USDT',

                payment_type TEXT,

                status TEXT,

                transaction_id TEXT,

                created_at TEXT

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
    payment_type,
    transaction_id=None
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT INTO payments

            (

                telegram_id,

                amount,

                payment_type,

                transaction_id,

                status,

                created_at

            )

            VALUES (?,?,?,?,?,?)

            """,

            (

                str(telegram_id),

                float(amount),

                payment_type,

                transaction_id,

                "PENDING",

                datetime.utcnow()
                .isoformat()

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def confirm_payment(
    transaction_id
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE payments

            SET status='SUCCESS'

            WHERE transaction_id=?

            """,

            (

                transaction_id,

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def reject_payment(
    transaction_id
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE payments

            SET status='FAILED'

            WHERE transaction_id=?

            """,

            (

                transaction_id,

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








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

            (

                str(telegram_id),

            )

        )



        rows = cursor.fetchall()



        conn.close()



        return rows



    except Exception as e:


        logger.exception(e)


        return []








def calculate_total_revenue():

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


            return round(

                float(result[0]),

                6

            )



        return 0



    except Exception as e:


        logger.exception(e)


        return 0








def get_monthly_revenue():

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(amount)

            FROM payments

            WHERE status='SUCCESS'

            AND created_at >= datetime('now','-30 days')

            """

        )



        result = cursor.fetchone()



        conn.close()



        return (

            float(result[0])

            if result[0]

            else 0

        )



    except Exception as e:


        logger.exception(e)


        return 0








def payment_report():

    try:


        return {


            "total":

                calculate_total_revenue(),


            "monthly":

                get_monthly_revenue()


        }



    except Exception as e:


        logger.exception(e)


        return {}
