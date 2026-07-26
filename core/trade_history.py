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

            if isinstance(row, dict):

                history.append(

                    {

                        "symbol": row.get("symbol"),

                        "side": row.get("side"),

                        "entry": row.get("entry"),

                        "tp": row.get("tp"),

                        "sl": row.get("sl"),

                        "quantity": row.get("quantity"),

                        "confidence": row.get("confidence"),

                        "pnl": row.get("pnl"),

                        "status": row.get("status"),

                        "created_at": row.get("created_at")

                    }

                )


            else:

                history.append(

                    {

                        "symbol": row[0],

                        "side": row[1],

                        "entry": row[2],

                        "tp": row[3],

                        "sl": row[4],

                        "quantity": row[5],

                        "confidence": row[6],

                        "pnl": row[7],

                        "status": row[8],

                        "created_at": row[9]

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
