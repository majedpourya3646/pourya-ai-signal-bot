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

        total_result = execute_query(
            """
            SELECT COUNT(*) AS total
            FROM performance
            """
        )


        wins_result = execute_query(
            """
            SELECT COUNT(*) AS wins
            FROM performance
            WHERE result='WIN'
            """
        )


        profit_result = execute_query(
            """
            SELECT COALESCE(SUM(pnl),0) AS profit
            FROM performance
            """
        )



        total = (
            total_result[0].get("total", 0)
            if total_result
            else 0
        )


        wins = (
            wins_result[0].get("wins", 0)
            if wins_result
            else 0
        )


        profit = (
            profit_result[0].get("profit", 0)
            if profit_result
            else 0
        )



        win_rate = 0


        if total > 0:

            win_rate = round(
                wins / total * 100,
                2
            )



        return {

            "total_trades": total,

            "wins": wins,

            "losses": total - wins,

            "win_rate": win_rate,

            "profit": round(
                float(profit),
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
