# core/subscription_manager.py

import sqlite3

from datetime import datetime, timedelta

from core.logger import logger



DB_PATH = "data/subscriptions.db"





def get_connection():

    try:

        return sqlite3.connect(
            DB_PATH
        )


    except Exception as e:


        logger.exception(e)


        return None






def init_subscription_database():

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS subscriptions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                plan TEXT DEFAULT 'FREE',

                start_date TEXT,

                expire_date TEXT,

                active INTEGER DEFAULT 0,

                max_trades INTEGER DEFAULT 1,

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






def create_subscription(
    telegram_id,
    plan="BASIC",
    days=30
):

    try:


        conn = get_connection()


        if not conn:

            return False



        start = datetime.utcnow()



        expire = (

            start

            +

            timedelta(
                days=days
            )

        )



        limits = {


            "FREE":

                1,


            "BASIC":

                3,


            "VIP":

                10


        }



        max_trades = limits.get(

            plan,

            1

        )



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT OR REPLACE INTO subscriptions

            (

                telegram_id,

                plan,

                start_date,

                expire_date,

                active,

                max_trades,

                created_at

            )

            VALUES (?,?,?,?,?,?,?)

            """,

            (

                telegram_id,

                plan,

                start.isoformat(),

                expire.isoformat(),

                1,

                max_trades,

                start.isoformat()

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


        if not conn:

            return None



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM subscriptions

            WHERE telegram_id=?

            """,

            (

                telegram_id,

            )

        )



        row = cursor.fetchone()



        conn.close()



        if not row:

            return None



        return {


            "id":

                row[0],


            "telegram_id":

                row[1],


            "plan":

                row[2],


            "start":

                row[3],


            "expire":

                row[4],


            "active":

                row[5],


            "max_trades":

                row[6]


        }



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



        expire = datetime.fromisoformat(

            subscription["expire"]

        )



        if datetime.utcnow() > expire:


            disable_subscription(
                telegram_id
            )


            return False



        return bool(

            subscription["active"]

        )



    except Exception as e:


        logger.exception(e)


        return False






def disable_subscription(
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

                telegram_id,

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def get_user_limit(
    telegram_id
):

    try:


        subscription = get_subscription(
            telegram_id
        )


        if not subscription:

            return 0



        return subscription.get(

            "max_trades",

            0

        )



    except Exception as e:


        logger.exception(e)


        return 0
