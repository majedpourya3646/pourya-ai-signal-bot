# core/performance_tracker.py

from core.database_manager import (
    execute_query
)

from core.logger import logger





def create_performance_table():

    try:

        execute_query(
            """
            CREATE TABLE IF NOT EXISTS performance (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                trade_id INTEGER,

                symbol TEXT,

                pnl REAL DEFAULT 0,

                result TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
            """
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def record_trade_result(
    trade_id,
    symbol,
    pnl
):

    try:

        result = (

            "WIN"

            if float(pnl) > 0

            else

            "LOSS"

        )



        execute_query(
            """
            INSERT INTO performance
            (
                trade_id,
                symbol,
                pnl,
                result
            )
            VALUES
            (?, ?, ?, ?)
            """,
            (
                trade_id,
                symbol,
                pnl,
                result
            )
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_statistics():

    try:

        total = execute_query(
            """
            SELECT COUNT(*)
            FROM performance
            """
        )[0][0]



        wins = execute_query(
            """
            SELECT COUNT(*)
            FROM performance
            WHERE result='WIN'
            """
        )[0][0]



        profit = execute_query(
            """
            SELECT COALESCE(SUM(pnl),0)
            FROM performance
            """
        )[0][0]



        win_rate = 0



        if total > 0:

            win_rate = round(

                wins

                /

                total

                *

                100,

                2

            )



        return {

            "total_trades": total,

            "wins": wins,

            "losses": total - wins,

            "win_rate": win_rate,

            "profit": round(

                profit,

                2

            )

        }



    except Exception as e:

        logger.exception(e)

        return {

            "total_trades": 0,

            "wins": 0,

            "losses": 0,

            "win_rate": 0,

            "profit": 0

        }
