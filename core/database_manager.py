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


        connection = sqlite3.connect(
            DATABASE_PATH
        )


        connection.row_factory = sqlite3.Row


        return connection


    except Exception as e:

        logger.exception(e)

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

                signal TEXT,

                order_id TEXT,

                entry REAL,

                tp REAL,

                sl REAL,

                quantity REAL,

                confidence REAL,

                status TEXT DEFAULT 'OPEN',

                pnl REAL DEFAULT 0,

                close_reason TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                closed_at TIMESTAMP

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

        logger.exception(e)

        return False





def execute_query(
    query,
    params=()
):

    connection = None


    try:

        connection = get_connection()


        if not connection:

            return []



        cursor = connection.cursor()



        cursor.execute(
            query,
            params
        )



        query_type = query.strip().upper()



        if query_type.startswith(
            "SELECT"
        ):

            rows = cursor.fetchall()


            return [
                dict(row)
                for row in rows
            ]



        connection.commit()


        return cursor.rowcount



    except Exception as e:

        logger.exception(e)

        return []



    finally:

        if connection:

            connection.close()
