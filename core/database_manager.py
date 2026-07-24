# core/database_manager.py

import sqlite3
import os

from core.logger import logger



DATABASE_PATH = "data/pourya_trader.db"



def get_connection():

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        return sqlite3.connect(
            DATABASE_PATH
        )



    except Exception as e:


        logger.exception(
            e
        )


        return None




def init_database():

    try:


        connection = get_connection()



        if not connection:

            return False



        cursor = connection.cursor()



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

                confidence REAL,

                status TEXT DEFAULT 'OPEN',

                pnl REAL DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

            """
        )



        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY,

                username TEXT,

                active INTEGER DEFAULT 1,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

            """
        )



        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS reports (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                type TEXT,

                content TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

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


        connection = get_connection()



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
