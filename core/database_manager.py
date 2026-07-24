# core/database_manager.py

import sqlite3
import os

from core.logger import logger



DATABASE_PATH = "data/pourya_trader.db"



def create_connection():

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        connection = sqlite3.connect(

            DATABASE_PATH

        )


        return connection



    except Exception as e:


        logger.exception(
            e
        )


        return None




def init_database():

    try:


        connection = create_connection()



        if not connection:

            return False



        cursor = connection.cursor()



        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY,

                username TEXT,

                active INTEGER DEFAULT 1,

                profit_share REAL DEFAULT 20,

                created_at TEXT

            )

            """
        )



        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS trades (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                side TEXT,

                entry REAL,

                tp REAL,

                sl REAL,

                quantity REAL,

                status TEXT,

                profit REAL DEFAULT 0,

                created_at TEXT

            )

            """
        )



        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS payments (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,

                amount REAL,

                type TEXT,

                created_at TEXT

            )

            """
        )



        connection.commit()


        connection.close()



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def execute_query(
    query,
    params=()
):

    try:


        connection = create_connection()



        cursor = connection.cursor()



        cursor.execute(

            query,

            params

        )


        connection.commit()



        result = cursor.fetchall()



        connection.close()



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return []
