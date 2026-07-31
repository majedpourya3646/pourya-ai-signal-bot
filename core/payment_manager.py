# core/payment_manager.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)





def create_payment(
    telegram_id,
    amount,
    currency="USDT",
    description=None
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

                currency,

                status,

                description,

                created_at

            )

            VALUES

            (?,?,?,?,?,?)

            """,

            (

                str(telegram_id),

                float(amount),

                currency,

                "PENDING",

                description,

                datetime.utcnow().isoformat()

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
    status
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE payments

            SET status=?

            WHERE id=?

            """,

            (

                status,

                payment_id

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def get_payment(
    payment_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM payments

            WHERE id=?

            """,

            (

                payment_id,

            )

        )



        row = cursor.fetchone()



        conn.close()



        if row:

            return dict(row)



        return None



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

            (

                str(telegram_id),

            )

        )



        rows = cursor.fetchall()



        conn.close()



        return [

            dict(row)

            for row in rows

        ]



    except Exception as e:


        logger.exception(e)


        return []









def confirm_payment(
    payment_id
):

    try:


        return update_payment_status(

            payment_id,

            "PAID"

        )



    except Exception as e:


        logger.exception(e)


        return False







def cancel_payment(
    payment_id
):

    try:


        return update_payment_status(

            payment_id,

            "CANCELLED"

        )



    except Exception as e:


        logger.exception(e)


        return False
