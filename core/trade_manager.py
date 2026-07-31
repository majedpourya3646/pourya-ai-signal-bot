# core/trade_manager.py

from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)








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


        conn = get_connection()

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

                opened_at

            )

            VALUES

            (?,?,?,?,?,?,?,?,?)

            """,

            (

                symbol,

                side,

                float(entry),

                float(tp),

                float(sl),

                float(quantity),

                float(confidence),

                "OPEN",

                datetime.utcnow().isoformat()

            )

        )



        trade_id = cursor.lastrowid



        conn.commit()

        conn.close()



        logger.info(

            f"TRADE OPENED {symbol}"

        )



        return trade_id



    except Exception as e:


        logger.exception(e)


        return None







def close_trade(
    trade_id,
    exit_price,
    pnl
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE trades

            SET

                status=?,

                pnl=?,

                closed_at=?

            WHERE id=?

            """,

            (

                "CLOSED",

                float(pnl),

                datetime.utcnow().isoformat(),

                trade_id

            )

        )



        conn.commit()

        conn.close()



        logger.info(

            f"TRADE CLOSED ID={trade_id}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def get_open_trades():

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM trades

            WHERE status='OPEN'

            ORDER BY id DESC

            """

        )



        rows = cursor.fetchall()



        conn.close()



        return [

            dict(row)

            for row in rows

        ]



    except Exception as e:


        logger.exception(e)


        return []









def get_trade_history(
    limit=100
):

    try:


        conn = get_connection()

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



        return [

            dict(row)

            for row in rows

        ]



    except Exception as e:


        logger.exception(e)


        return []









def get_trade_by_id(
    trade_id
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT *

            FROM trades

            WHERE id=?

            """,

            (

                trade_id,

            )

        )



        row = cursor.fetchone()



        conn.close()



        if row:

            return dict(row)



        return None



    except Exception as e:


        logger.exception(e)


        return None







def count_open_trades():

    try:


        return len(

            get_open_trades()

        )



    except Exception as e:


        logger.exception(e)


        return 0
