# core/trade_manager.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



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
                confidence,
                status
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, 'OPEN')
            """,
            (
                symbol,
                side,
                entry,
                tp,
                sl,
                quantity,
                confidence
            )
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False





def get_trade(
    symbol
):

    try:

        result = execute_query(
            """
            SELECT
                symbol,
                side,
                entry,
                tp,
                sl,
                quantity,
                confidence,
                status
            FROM trades
            WHERE symbol=?
            AND status='OPEN'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                symbol,
            )
        )

        if not result:

            return None

        row = result[0]

        return {

            "symbol": row[0],

            "side": row[1],

            "entry": row[2],

            "tp": row[3],

            "sl": row[4],

            "quantity": row[5],

            "confidence": row[6],

            "status": row[7]

        }

    except Exception as e:

        logger.exception(e)

        return None





def can_buy(
    symbol
):

    try:

        return get_trade(
            symbol
        ) is None

    except Exception as e:

        logger.exception(e)

        return False





def close_trade(
    symbol,
    exit_price,
    pnl
):

    try:

        execute_query(
            """
            UPDATE trades
            SET
                status='CLOSED',
                pnl=?
            WHERE symbol=?
            AND status='OPEN'
            """,
            (
                pnl,
                symbol
            )
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False





def get_open_trades():

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
                confidence
            FROM trades
            WHERE status='OPEN'
            """
        )

        trades = []

        for row in rows:

            trades.append(

                {

                    "symbol": row[0],

                    "side": row[1],

                    "entry": row[2],

                    "tp": row[3],

                    "sl": row[4],

                    "quantity": row[5],

                    "confidence": row[6]

                }

            )

        return trades

    except Exception as e:

        logger.exception(e)

        return []





def total_open_trades():

    return len(
        get_open_trades()
    )
