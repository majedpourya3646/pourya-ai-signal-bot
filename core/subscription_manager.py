# core/subscription_manager.py

import sqlite3

from datetime import datetime, timedelta

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









def init_subscription_database():

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS subscriptions

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

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



        expire = start + timedelta(

            days=days

        )



        cursor.execute(

            """

            INSERT INTO subscriptions

            (

                telegram_id,

                plan,

                start_date,

                expire_date

            )

            VALUES (?,?,?,?)

            """,

            (

                str(telegram_id),

                plan,

                start.isoformat(),

                expire.isoformat()

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

            ORDER BY id DESC

            LIMIT 1

            """,

            (

                str(telegram_id),

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


            "start_date":

                row[3],


            "expire_date":

                row[4],


            "active":

                row[5]

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

            subscription["expire_date"]

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

                str(telegram_id),

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def upgrade_subscription(
    telegram_id,
    plan,
    days
):

    try:


        disable_subscription(

            telegram_id

        )



        return create_subscription(

            telegram_id,

            plan,

            days

        )



    except Exception as e:


        logger.exception(e)


        return False








def get_plan_limits(
    plan
):

    plans = {


        "FREE":

            {

                "max_trades":1,

                "risk":0.5

            },


        "VIP":

            {

                "max_trades":10,

                "risk":2

            },


        "PRO":

            {

                "max_trades":50,

                "risk":3

            }

    }



    return plans.get(

        plan,

        plans["FREE"]

    )
