# core/database_manager.py

import sqlite3
import os

from datetime import datetime

from core.logger import logger




DATABASE_DIR = "data"

DATABASE_FILE = os.path.join(

    DATABASE_DIR,

    "pourya_trader.db"

)







def create_database_directory():

    try:


        if not os.path.exists(
            DATABASE_DIR
        ):


            os.makedirs(
                DATABASE_DIR
            )



        return True



    except Exception as e:


        logger.exception(e)


        return False






def get_connection():

    try:


        create_database_directory()



        conn = sqlite3.connect(

            DATABASE_FILE,

            check_same_thread=False

        )


        return conn



    except Exception as e:


        logger.exception(e)


        return None






def create_tables():

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

                user_profit_percent REAL DEFAULT 50,

                created_at TEXT

            )

            """

        )





        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS trades (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                symbol TEXT,

                side TEXT,

                entry REAL,

                exit REAL,

                quantity REAL,

                leverage REAL,

                pnl REAL DEFAULT 0,

                status TEXT,

                created_at TEXT,

                closed_at TEXT

            )

            """

        )





        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS payments (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                amount REAL,

                plan TEXT,

                status TEXT,

                created_at TEXT

            )

            """

        )





        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS system_logs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                event TEXT,

                details TEXT,

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







def insert_log(
    event,
    details=None
):

    try:


        conn = get_connection()



        cursor = conn.cursor()



        cursor.execute(

            """

            INSERT INTO system_logs

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

                datetime.utcnow().isoformat()

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def database_status():

    try:


        conn = get_connection()



        if not conn:

            return False



        conn.close()



        return True



    except:


        return False






def initialize_database():

    try:


        return create_tables()



    except Exception as e:


        logger.exception(e)


        return False
