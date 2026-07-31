# core/database_manager.py

import sqlite3

import os

from core.logger import logger





DB_PATH = "data/pourya_trader.db"









def ensure_directory():

    try:


        folder = os.path.dirname(

            DB_PATH

        )



        if folder and not os.path.exists(folder):

            os.makedirs(

                folder

            )



    except Exception as e:


        logger.exception(e)









def get_connection():

    try:


        ensure_directory()



        conn = sqlite3.connect(

            DB_PATH,

            check_same_thread=False

        )



        conn.row_factory = sqlite3.Row



        return conn



    except Exception as e:


        logger.exception(e)


        return None










def initialize_database():

    try:


        conn = get_connection()

        cursor = conn.cursor()






        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS trades

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                side TEXT,

                entry REAL,

                tp REAL,

                sl REAL,

                quantity REAL,

                confidence REAL,

                pnl REAL DEFAULT 0,

                status TEXT,

                opened_at TEXT,

                closed_at TEXT

            )

            """

        )







        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS users

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                username TEXT,

                trading_mode TEXT,

                profit_percent REAL,

                active INTEGER,

                created_at TEXT

            )

            """

        )







        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS subscriptions

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                plan TEXT,

                start_date TEXT,

                expire_date TEXT,

                active INTEGER

            )

            """

        )







        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS payments

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                amount REAL,

                currency TEXT,

                status TEXT,

                description TEXT,

                created_at TEXT

            )

            """

        )







        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS profits

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                trade_id INTEGER,

                gross_profit REAL,

                user_profit REAL,

                system_profit REAL,

                created_at TEXT

            )

            """

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







def database_status():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            "SELECT 1"

        )



        result = cursor.fetchone()



        conn.close()



        return result is not None



    except Exception as e:


        logger.exception(e)


        return False







def reset_database():

    try:


        if os.path.exists(

            DB_PATH

        ):

            os.remove(

                DB_PATH

            )



        return initialize_database()



    except Exception as e:


        logger.exception(e)


        return False
