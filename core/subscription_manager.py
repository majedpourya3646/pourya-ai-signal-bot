# core/subscription_manager.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)





def create_subscription(
    telegram_id,
    plan,
    start_date,
    expire_date
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



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

            VALUES

            (?,?,?,?,?)

            """,

            (

                str(telegram_id),

                plan,

                start_date,

                expire_date,

                1

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def get_subscription(
    telegram_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM subscriptions

            WHERE telegram_id=?

            """,

            (

                str(telegram_id),

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







def check_subscription(
    telegram_id
):

    try:


        subscription = get_subscription(

            telegram_id

        )



        if not subscription:

            return False





        if subscription.get(

            "active"

        ) != 1:

            return False





        expire = subscription.get(

            "expire_date"

        )



        if not expire:

            return False





        now = datetime.utcnow()



        expire_time = datetime.fromisoformat(

            expire

        )



        if now > expire_time:


            deactivate_subscription(

                telegram_id

            )


            return False





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

            (

                str(telegram_id),

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def activate_subscription(
    telegram_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE subscriptions

            SET active=1

            WHERE telegram_id=?

            """,

            (

                str(telegram_id),

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def get_active_subscriptions():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM subscriptions

            WHERE active=1

            """

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
