# core/database_manager.py

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








def initialize_database():

    try:


        conn = get_connection()



        if not conn:


            return False



        cursor = conn.cursor()





        tables = [

        """

        CREATE TABLE IF NOT EXISTS logs

        (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event TEXT,

            details TEXT,

            created_at TEXT

        )

        """,



        """

        CREATE TABLE IF NOT EXISTS trades

        (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            telegram_id TEXT,

            symbol TEXT,

            side TEXT,

            entry REAL,

            exit REAL,

            quantity REAL,

            tp REAL,

            sl REAL,

            pnl REAL,

            status TEXT,

            created_at TEXT,

            closed_at TEXT

        )

        """,



        """

        CREATE TABLE IF NOT EXISTS settings

        (

            key TEXT PRIMARY KEY,

            value TEXT

        )

        """,



        ]





        for table in tables:


            cursor.execute(

                table

            )



        conn.commit()

        conn.close()



        logger.info(

            "DATABASE INITIALIZED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def insert_log(
    event,
    details
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT INTO logs

            (

                event,

                details,

                created_at

            )

            VALUES (?,?,?)

            """,

            (

                event,

                str(details),

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








def get_logs():

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM logs

            ORDER BY id DESC

            """

        )



        rows = cursor.fetchall()



        conn.close()



        return rows



    except Exception as e:


        logger.exception(e)


        return []








def save_setting(
    key,
    value
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT OR REPLACE INTO settings

            (

                key,

                value

            )

            VALUES (?,?)

            """,

            (

                key,

                str(value)

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False








def get_setting(
    key,
    default=None
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT value

            FROM settings

            WHERE key=?

            """,

            (

                key,

            )

        )



        result = cursor.fetchone()



        conn.close()



        if result:


            return result[0]



        return default



    except Exception as e:


        logger.exception(e)


        return default








def database_status():

    try:


        conn = get_connection()



        if conn:


            conn.close()



            return True



        return False



    except Exception as e:


        logger.exception(e)


        return False
