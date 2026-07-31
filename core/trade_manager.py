# core/trade_manager.py

from datetime import datetime

from core.database_manager import (
    get_connection
)

from core.logger import logger






def open_trade(
    symbol,
    side,
    entry,
    tp,
    sl,
    quantity,
    confidence,
    telegram_id=None
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            SELECT id

            FROM trades

            WHERE symbol=?

            AND status='OPEN'

            """,

            (

                symbol,

            )

        )



        exists = cursor.fetchone()



        if exists:

            conn.close()

            logger.warning(

                f"TRADE ALREADY OPEN {symbol}"

            )

            return False






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

        return False









def close_trade(
    trade_id,
    exit_price=None,
    pnl=0
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE trades

            SET

            exit=?,

            pnl=?,

            status='CLOSED',

            closed_at=?

            WHERE id=?

            """,

            (

                exit_price,

                float(pnl),

                datetime.utcnow().isoformat(),

                trade_id

            )

        )



        conn.commit()

        conn.close()



        logger.info(

            f"TRADE CLOSED {trade_id}"

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



        trades = []



        for row in rows:


            trades.append(

                dict(row)

            )



        return trades



    except Exception as e:


        logger.exception(e)

        return []











def get_trade(
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



        if not row:

            return None



        return dict(row)



    except Exception as e:


        logger.exception(e)

        return None











def update_trade_pnl(
    trade_id,
    pnl
):

    try:


        conn = get_connection()

        cursor = conn.cursor()



        cursor.execute(

            """

            UPDATE trades

            SET pnl=?

            WHERE id=?

            """,

            (

                float(pnl),

                trade_id

            )

        )



        conn.commit()

        conn.close()



        return True



    except Exception as e:


        logger.exception(e)

        return False











def count_open_positions():

    try:


        return len(

            get_open_trades()

        )



    except Exception:


        return 0











def get_trade_history(
    limit=50
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
