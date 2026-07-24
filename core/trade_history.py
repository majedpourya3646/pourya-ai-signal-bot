# core/trade_history.py

from datetime import datetime

from core.database_manager import (
    execute_query
)

from core.logger import logger



def save_trade_history(
    symbol,
    side,
    entry,
    tp,
    sl,
    quantity,
    status="OPEN"
):

    try:


        execute_query(

            """

            INSERT INTO trades

            (

                symbol,

                side,

                entry,

                tp,

                sl,

                quantity,

                status,

                created_at

            )

            VALUES

            (?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                symbol,

                side,

                entry,

                tp,

                sl,

                quantity,

                status,

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            )

        )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def close_trade_history(
    trade_id,
    profit,
    status="CLOSED"
):

    try:


        execute_query(

            """

            UPDATE trades

            SET

            status = ?,

            profit = ?

            WHERE id = ?

            """,

            (

                status,

                profit,

                trade_id

            )

        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def get_trade_history(
    limit=50
):

    try:


        result = execute_query(

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


        return result



    except Exception as e:


        logger.exception(
            e
        )


        return []




def get_total_profit():

    try:


        result = execute_query(

            """

            SELECT

            SUM(profit)

            FROM trades

            WHERE status='CLOSED'

            """

        )



        if result and result[0][0]:

            return round(

                float(result[0][0]),

                2

            )



        return 0



    except Exception as e:


        logger.exception(
            e
        )


        return 0
