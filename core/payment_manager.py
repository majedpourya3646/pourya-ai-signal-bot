# core/payment_manager.py

import sqlite3

from datetime import datetime

from core.logger import logger

from core.subscription_manager import (
    create_subscription
)



DB_PATH = "data/payments.db"





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


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS payments (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                amount REAL,

                currency TEXT DEFAULT 'USDT',

                plan TEXT,

                payment_id TEXT,

                status TEXT DEFAULT 'PENDING',

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
    plan,
    payment_id
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT INTO payments

            (

                telegram_id,

                amount,

                plan,

                payment_id,

                status,

                created_at

            )

            VALUES (?,?,?,?,?,?)

            """,

            (

                telegram_id,

                amount,

                plan,

                payment_id,

                "PENDING",

                datetime.utcnow().isoformat()

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def confirm_payment(
    payment_id
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM payments

            WHERE payment_id=?

            """,

            (

                payment_id,

            )

        )



        payment = cursor.fetchone()



        if not payment:


            conn.close()


            return False



        telegram_id = payment[1]

        plan = payment[3]



        cursor.execute(

            """

            UPDATE payments

            SET status='PAID'

            WHERE payment_id=?

            """,

            (

                payment_id,

            )

        )



        conn.commit()

        conn.close()



        create_subscription(

            telegram_id,

            plan,

            30

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def reject_payment(
    payment_id
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE payments

            SET status='FAILED'

            WHERE payment_id=?

            """,

            (

                payment_id,

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def get_payment_history(
    telegram_id=None
):

    try:


        conn = get_connection()


        if not conn:

            return []



        cursor = conn.cursor()



        if telegram_id:


            cursor.execute(

                """

                SELECT *

                FROM payments

                WHERE telegram_id=?

                ORDER BY id DESC

                """,

                (

                    telegram_id,

                )

            )


        else:


            cursor.execute(

                """

                SELECT *

                FROM payments

                ORDER BY id DESC

                """

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


        if not conn:

            return 0



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT SUM(amount)

            FROM payments

            WHERE status='PAID'

            """

        )



        result = cursor.fetchone()



        conn.close()



        return float(

            result[0] or 0

        )



    except Exception as e:


        logger.exception(e)


        return 0
