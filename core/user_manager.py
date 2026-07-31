# core/user_manager.py

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






def init_user_database():

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                username TEXT,

                active INTEGER DEFAULT 1,

                trading_mode TEXT DEFAULT 'AUTO',

                notification_level TEXT DEFAULT 'BASIC',

                risk_percent REAL DEFAULT 1,

                leverage REAL DEFAULT 10,

                user_profit_percent REAL DEFAULT 50,

                email TEXT,

                phone TEXT,

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






def create_user(
    telegram_id,
    username=None
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT OR IGNORE INTO users

            (

                telegram_id,

                username,

                created_at

            )

            VALUES (?,?,?)

            """,

            (

                str(telegram_id),

                username,

                datetime.utcnow().isoformat()

            )

        )



        conn.commit()

        conn.close()



        return True



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



        if not row:

            return None



        return {


            "id":

                row[0],


            "telegram_id":

                row[1],


            "username":

                row[2],


            "active":

                row[3],


            "trading_mode":

                row[4],


            "notification_level":

                row[5],


            "risk_percent":

                row[6],


            "leverage":

                row[7],


            "user_profit_percent":

                row[8],


            "email":

                row[9],


            "phone":

                row[10]


        }



    except Exception as e:


        logger.exception(e)


        return None






def update_user_setting(
    telegram_id,
    key,
    value
):

    try:


        allowed = [

            "active",

            "trading_mode",

            "notification_level",

            "risk_percent",

            "leverage",

            "user_profit_percent",

            "email",

            "phone"

        ]



        if key not in allowed:


            return False



        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            f"""

            UPDATE users

            SET {key}=?

            WHERE telegram_id=?

            """,

            (

                value,

                str(telegram_id)

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def get_all_active_users():

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



        return rows



    except Exception as e:


        logger.exception(e)


        return []








def deactivate_user(
    telegram_id
):

    return update_user_setting(

        telegram_id,

        "active",

        0

    )








def activate_user(
    telegram_id
):

    return update_user_setting(

        telegram_id,

        "active",

        1

    )
