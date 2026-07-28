# core/trade_manager.py

import sqlite3
import os
from datetime import datetime

from core.logger import logger



DB_PATH = "data/trades.db"




def init_db():

    try:

        os.makedirs(
            "data",
            exist_ok=True
        )


        conn = sqlite3.connect(
            DB_PATH
        )


        cursor = conn.cursor()



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

                status TEXT,

                created_at TEXT,

                closed_at TEXT DEFAULT NULL

            )
            """
        )



        conn.commit()

        conn.close()



    except Exception as e:

        logger.exception(e)





def open_trade(
    symbol,
    side,
    entry,
    tp,
    sl,
    quantity,
    confidence
):

    try:


        init_db()



        conn = sqlite3.connect(
            DB_PATH
        )


        cursor = conn.cursor()



        cursor.execute(

            """
            INSERT INTO trades
            (
                symbol,
                side,
                entry,
                tp,
                sl,
                quantity,
                confidence,
                status,
                created_at
            )

            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )

            """,

            (

                symbol,

                side,

                float(entry),

                float(tp)
                if tp
                else 0,

                float(sl)
                if sl
                else 0,

                float(quantity),

                float(confidence),

                "OPEN",

                datetime.utcnow().isoformat()

            )

        )



        conn.commit()

        conn.close()



        logger.info(

            f"TRADE SAVED {symbol}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False





def get_open_trades():

    try:


        init_db()



        conn = sqlite3.connect(
            DB_PATH
        )


        cursor = conn.cursor()



        cursor.execute(

            """
            SELECT *

            FROM trades

            WHERE status='OPEN'

            """

        )



        rows = cursor.fetchall()



        conn.close()



        return [

            {

                "id": row[0],

                "symbol": row[1],

                "side": row[2],

                "entry": row[3],

                "tp": row[4],

                "sl": row[5],

                "quantity": row[6],

                "confidence": row[7],

                "status": row[8],

                "created_at": row[9]

            }

            for row in rows

        ]



    except Exception as e:


        logger.exception(e)


        return []







def close_trade(
    trade_id
):

    try:


        conn = sqlite3.connect(
            DB_PATH
        )


        cursor = conn.cursor()



        cursor.execute(

            """
            UPDATE trades

            SET

            status='CLOSED',

            closed_at=?

            WHERE id=?

            """,

            (

                datetime.utcnow().isoformat(),

                trade_id

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False





def get_trade_history():

    try:


        conn = sqlite3.connect(
            DB_PATH
        )


        cursor = conn.cursor()



        cursor.execute(

            """
            SELECT *

            FROM trades

            ORDER BY id DESC

            """

        )



        rows = cursor.fetchall()



        conn.close()



        return rows



    except Exception as e:


        logger.exception(e)


        return []
