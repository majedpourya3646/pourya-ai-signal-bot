# core/trade_history.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



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

        logger.exception(e)

        return []





def get_closed_trades():

    try:

        return execute_query(
            """
            SELECT *
            FROM trades
            WHERE status='CLOSED'
            ORDER BY id DESC
            """
        )



    except Exception as e:

        logger.exception(e)

        return []





def get_open_trades():

    try:

        return execute_query(
            """
            SELECT *
            FROM trades
            WHERE status='OPEN'
            ORDER BY id DESC
            """
        )



    except Exception as e:

        logger.exception(e)

        return []





def count_trades():

    try:

        result = execute_query(
            """
            SELECT COUNT(*) as total
            FROM trades
            """
        )


        if not result:

            return 0


        return result[0].get(
            "total",
            0
        )



    except Exception as e:

        logger.exception(e)

        return 0
