# core/performance_tracker.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def get_statistics():

    try:

        total = execute_query(
            """
            SELECT COUNT(*)
            FROM trades
            """
        )[0][0]



        open_trades = execute_query(
            """
            SELECT COUNT(*)
            FROM trades
            WHERE status='OPEN'
            """
        )[0][0]



        closed = execute_query(
            """
            SELECT COUNT(*)
            FROM trades
            WHERE status='CLOSED'
            """
        )[0][0]



        wins = execute_query(
            """
            SELECT COUNT(*)
            FROM trades
            WHERE status='CLOSED'
            AND pnl > 0
            """
        )[0][0]



        losses = execute_query(
            """
            SELECT COUNT(*)
            FROM trades
            WHERE status='CLOSED'
            AND pnl <= 0
            """
        )[0][0]



        pnl = execute_query(
            """
            SELECT
                COALESCE(SUM(pnl),0)
            FROM trades
            """
        )[0][0]



        win_rate = 0



        if closed > 0:

            win_rate = round(

                wins
                /
                closed
                *
                100,

                2

            )



        return {

            "total_trades": total,

            "open_trades": open_trades,

            "closed_trades": closed,

            "wins": wins,

            "losses": losses,

            "win_rate": win_rate,

            "profit": pnl

        }



    except Exception as e:

        logger.exception(e)

        return {}





def get_total_profit():

    try:

        return get_statistics().get(
            "profit",
            0
        )

    except Exception as e:

        logger.exception(e)

        return 0
