# core/trade_manager.py

import sqlite3

from datetime import datetime

from core.logger import logger



DB_PATH = "data/trades.db"




def get_connection():

    try:

        return sqlite3.connect(
            DB_PATH
        )


    except Exception as e:

        logger.exception(e)

        return None






def init_trade_database():

    try:

        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                side TEXT,

                entry REAL,

                exit REAL,

                tp REAL,

                sl REAL,

                quantity REAL,

                leverage REAL,

                confidence REAL,

                pnl REAL DEFAULT 0,

                pnl_percent REAL DEFAULT 0,

                user_profit REAL DEFAULT 0,

                software_profit REAL DEFAULT 0,

                status TEXT DEFAULT 'OPEN',

                reason TEXT,

                created_at TEXT,

                closed_at TEXT

            )
            """
        )


        conn.commit()

        conn.close()


        return True



    except Exception as e:


        logger.exception(e)


        return False






def open_trade(
    symbol,
    side,
    entry,
    tp,
    sl,
    quantity,
    confidence,
    leverage=1
):

    try:


        conn = get_connection()


        if not conn:

            return False



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
                leverage,
                confidence,
                status,
                created_at
            )

            VALUES (?,?,?,?,?,?,?,?,?,?)

            """,

            (

                symbol,

                side,

                entry,

                tp,

                sl,

                quantity,

                leverage,

                confidence,

                "OPEN",

                datetime.utcnow().isoformat()

            )

        )



        conn.commit()

        conn.close()



        logger.info(
            f"TRADE SAVED {symbol} {side}"
        )


        return True



    except Exception as e:


        logger.exception(e)


        return False






def get_open_trades():

    try:


        conn = get_connection()


        if not conn:

            return []



        cursor = conn.cursor()



        cursor.execute(

            """
            SELECT *

            FROM trades

            WHERE status='OPEN'

            """

        )


        rows = cursor.fetchall()



        columns = [

            "id",
            "symbol",
            "side",
            "entry",
            "exit",
            "tp",
            "sl",
            "quantity",
            "leverage",
            "confidence",
            "pnl",
            "pnl_percent",
            "user_profit",
            "software_profit",
            "status",
            "reason",
            "created_at",
            "closed_at"

        ]



        trades = []


        for row in rows:

            trades.append(
                dict(
                    zip(
                        columns,
                        row
                    )
                )
            )



        conn.close()



        return trades



    except Exception as e:


        logger.exception(e)


        return []






def close_trade(
    trade_id,
    exit_price=None,
    pnl=0,
    pnl_percent=0,
    reason="CLOSED"
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """
            UPDATE trades

            SET

            exit=?,

            pnl=?,

            pnl_percent=?,

            status=?,

            reason=?,

            closed_at=?

            WHERE id=?

            """,

            (

                exit_price,

                pnl,

                pnl_percent,

                "CLOSED",

                reason,

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






def update_profit_share(
    trade_id,
    user_profit,
    software_profit
):

    try:


        conn = get_connection()


        if not conn:

            return False



        cursor = conn.cursor()



        cursor.execute(

            """
            UPDATE trades

            SET

            user_profit=?,

            software_profit=?

            WHERE id=?

            """,

            (

                user_profit,

                software_profit,

                trade_id

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)


        return False






def get_trade_history(
    limit=50
):

    try:


        conn = get_connection()


        if not conn:

            return []



        cursor = conn.cursor()



        cursor.execute(

            """
            SELECT *

            FROM trades

            ORDER BY id DESC

            LIMIT ?

            """,

            (
                limit,
            )

        )


        rows = cursor.fetchall()



        conn.close()



        return rows



    except Exception as e:


        logger.exception(e)


        return []
