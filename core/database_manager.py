# core/database_manager.py

import sqlite3

import os

from core.logger import logger

from config import DATABASE_PATH





def ensure_database_folder():

    try:

        folder = os.path.dirname(

            DATABASE_PATH

        )


        if folder and not os.path.exists(folder):

            os.makedirs(folder)


        return True


    except Exception as e:

        logger.exception(e)

        return False








def get_connection():

    try:

        ensure_database_folder()


        conn = sqlite3.connect(

            DATABASE_PATH,

            check_same_thread=False

        )


        conn.row_factory = sqlite3.Row


        return conn



    except Exception as e:

        logger.exception(e)

        return None









def init_database():

    try:

        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        # Trades

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS trades

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                side TEXT,

                entry REAL,

                exit REAL,

                tp REAL,

                sl REAL,

                quantity REAL,

                confidence REAL,

                pnl REAL DEFAULT 0,

                status TEXT DEFAULT 'OPEN',

                created_at TEXT,

                closed_at TEXT

            )

            """

        )





        # Users

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS users

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                username TEXT,

                email TEXT,

                phone TEXT,

                trading_mode TEXT DEFAULT 'MANUAL',

                profit_percent REAL DEFAULT 50,

                active INTEGER DEFAULT 1,

                created_at TEXT

            )

            """

        )





        # Profits

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS profits

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                trade_id INTEGER,

                gross_profit REAL,

                user_profit REAL,

                software_profit REAL,

                created_at TEXT

            )

            """

        )





        # Subscriptions

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS subscriptions

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT UNIQUE,

                plan TEXT,

                start_date TEXT,

                expire_date TEXT,

                active INTEGER DEFAULT 1

            )

            """

        )





        # Payments

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS payments

            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                telegram_id TEXT,

                amount REAL,

                currency TEXT,

                payment_method TEXT,

                transaction_id TEXT,

                status TEXT,

                description TEXT,

                created_at TEXT,

                updated_at TEXT

            )

            """

        )





        # Settings

        cursor.execute(

            """

            CREATE TABLE IF NOT EXISTS settings

            (

                key TEXT PRIMARY KEY,

                value TEXT

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


        if not conn:

            return False



        cursor = conn.cursor()


        cursor.execute(

            "SELECT 1"

        )


        result = cursor.fetchone()


        conn.close()



        return bool(result)



    except Exception as e:

        logger.exception(e)

        return False








def execute_query(
    query,
    params=()
):

    try:

        conn = get_connection()


        cursor = conn.cursor()



        cursor.execute(

            query,

            params

        )



        conn.commit()



        result = cursor.fetchall()



        conn.close()



        return result



    except Exception as e:

        logger.exception(e)

        return []








def backup_database():

    try:

        from core.backup_manager import (
            create_database_backup
        )


        return create_database_backup()



    except Exception as e:

        logger.exception(e)

        return False
