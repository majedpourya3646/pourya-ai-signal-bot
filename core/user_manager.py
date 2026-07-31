# core/user_manager.py

import sqlite3

from datetime import datetime

from core.logger import logger



DB_PATH = "data/users.db"




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

                email TEXT,

                phone TEXT,

                notification_level TEXT DEFAULT 'BASIC',

                user_profit_percent REAL DEFAULT 50,

                risk_percent REAL DEFAULT 1,

                leverage INTEGER DEFAULT 10,

                trading_mode TEXT DEFAULT 'AUTO',

                active INTEGER DEFAULT 1,

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

                telegram_id,

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


        if not conn:

            return None



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM users

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



        columns = [

            "id",

            "telegram_id",

            "username",

            "email",

            "phone",

            "notification_level",

            "user_profit_percent",

            "risk_percent",

            "leverage",

            "trading_mode",

            "active",

            "created_at"

        ]



        return dict(
            zip(
                columns,
                row
            )
        )



    except Exception as e:


        logger.exception(e)


        return None






def update_user_setting(
    telegram_id,
    key,
    value
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        allowed = [

            "notification_level",

            "user_profit_percent",

            "risk_percent",

            "leverage",

            "trading_mode",

            "email",

            "phone"

        ]



        if key not in allowed:

            return False



        cursor.execute(

            f"""

            UPDATE users

            SET {key}=?

            WHERE telegram_id=?

            """,

            (

                value,

                telegram_id

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


        if not conn:

            return []



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
