# core/trade_history.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def get_trade_history(
    limit=100
):

    try:

        rows = execute_query(
            """
            SELECT

                symbol,

                side,

                entry,

                tp,

                sl,

                quantity,

                confidence,

                pnl,

                status,

                created_at

            FROM trades

            ORDER BY id DESC

            LIMIT ?

            """,
            (
                limit,
            )
        )



        history = []



        for row in rows:

            history.append(

                {

                    "symbol": row.get(
                        "symbol"
                    ),

                    "side": row.get(
                        "side"
                    ),

                    "entry": row.get(
                        "entry"
                    ),

                    "tp": row.get(
                        "tp"
                    ),

                    "sl": row.get(
                        "sl"
                    ),

                    "quantity": row.get(
                        "quantity"
                    ),

                    "confidence": row.get(
                        "confidence"
                    ),

                    "pnl": row.get(
                        "pnl",
                        0
                    ),

                    "status": row.get(
                        "status"
                    ),

                    "created_at": row.get(
                        "created_at"
                    )

                }

            )



        return history



    except Exception as e:

        logger.exception(e)

        return []





def get_last_trade():

    try:

        history = get_trade_history(
            1
        )


        if history:

            return history[0]


        return None



    except Exception as e:

        logger.exception(e)

        return None
