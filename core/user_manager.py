# core/user_manager.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)

from config import (
    DEFAULT_USER_PROFIT_SHARE
)





def create_user(
    telegram_id,
    username=None
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT id

            FROM users

            WHERE telegram_id=?

            """,

            (

                str(telegram_id),

            )

        )



        exists = cursor.fetchone()



        if exists:

            conn.close()

            return exists[0]





        cursor.execute(

            """

            INSERT INTO users

            (

                telegram_id,

                username,

                trading_mode,

                profit_percent,

                active,

                created_at

            )

            VALUES

            (?,?,?,?,?,?)

            """,

            (

                str(telegram_id),

                username,

                "MANUAL",

                DEFAULT_USER_PROFIT_SHARE,

                1,

                datetime.utcnow().isoformat()

            )

        )



        user_id = cursor.lastrowid



        conn.commit()

        conn.close()



        return user_id



    except Exception as e:


        logger.exception(e)


        return False







def get_user(
    telegram_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM users

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







def update_trading_mode(
    telegram_id,
    mode
):

    try:


        mode = str(

            mode

        ).upper()



        if mode not in [

            "AUTO",

            "MANUAL"

        ]:

            return False





        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE users

            SET trading_mode=?

            WHERE telegram_id=?

            """,

            (

                mode,

                str(telegram_id)

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def update_profit_share(
    telegram_id,
    percent
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE users

            SET profit_percent=?

            WHERE telegram_id=?

            """,

            (

                float(percent),

                str(telegram_id)

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def deactivate_user(
    telegram_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE users

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







def activate_user(
    telegram_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE users

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







def get_active_users():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM users

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
