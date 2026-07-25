# core/performance.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def add_trade(
    symbol,
    signal,
    entry,
    tp,
    sl,
    exit_price,
    pnl,
    quantity,
    confidence,
    grade
):

    try:

        execute_query(
            """
            INSERT INTO reports
            (
                type,
                content
            )
            VALUES
            (
                ?,
                ?
            )
            """,
            (
                "TRADE",
                str(
                    {
                        "symbol": symbol,
                        "signal": signal,
                        "entry": entry,
                        "tp": tp,
                        "sl": sl,
                        "exit": exit_price,
                        "pnl": pnl,
                        "quantity": quantity,
                        "confidence": confidence,
                        "grade": grade
                    }
                )
            )
        )


        logger.info(
            f"TRADE RECORDED {symbol}"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_performance():

    try:

        trades = execute_query(
            """
            SELECT *
            FROM trades
            WHERE status='CLOSED'
            """
        )


        total = len(
            trades
        )


        wins = 0

        losses = 0

        profit = 0



        for trade in trades:

            pnl = float(
                trade.get(
                    "pnl",
                    0
                )
            )


            profit += pnl


            if pnl > 0:

                wins += 1


            elif pnl < 0:

                losses += 1



        win_rate = 0


        if total > 0:

            win_rate = (
                wins / total
            ) * 100



        return {

            "total_trades": total,

            "wins": wins,

            "losses": losses,

            "profit": round(
                profit,
                4
            ),

            "win_rate": round(
                win_rate,
                2
            )

        }



    except Exception as e:

        logger.exception(e)

        return {

            "total_trades": 0,

            "wins": 0,

            "losses": 0,

            "profit": 0,

            "win_rate": 0

        }
