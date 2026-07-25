# core/trade_manager.py

from datetime import datetime

from core.database_manager import (
    execute_query
)

from core.logger import logger



def can_buy(
    symbol
):

    try:

        result = execute_query(
            """
            SELECT id
            FROM trades
            WHERE symbol=?
            AND status='OPEN'
            LIMIT 1
            """,
            (
                symbol,
            )
        )


        return len(result) == 0


    except Exception as e:

        logger.exception(e)

        return False





def open_trade(
    symbol,
    side,
    entry,
    quantity,
    confidence=0,
    signal="",
    order_id=None,
    tp=0,
    sl=0
):

    try:

        execute_query(
            """
            INSERT INTO trades
            (
                symbol,
                side,
                signal,
                order_id,
                entry,
                tp,
                sl,
                quantity,
                confidence,
                status
            )

            VALUES
            (
                ?,?,?,?,?,?,?,?,?,?
            )
            """,
            (
                symbol,
                side,
                signal,
                str(order_id)
                if order_id
                else None,
                float(entry),
                float(tp),
                float(sl),
                float(quantity),
                float(confidence),
                "OPEN"
            )
        )


        logger.info(
            f"OPEN TRADE {symbol} {side}"
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
            SELECT *
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


        return result[0]



    except Exception as e:

        logger.exception(e)

        return None





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





def update_trade_pnl(
    symbol,
    pnl
):

    try:

        execute_query(
            """
            UPDATE trades
            SET pnl=?
            WHERE symbol=?
            AND status='OPEN'
            """,
            (
                float(pnl),
                symbol
            )
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False





def close_trade(
    symbol,
    exit_price,
    reason="MANUAL"
):

    try:

        trade = get_trade(
            symbol
        )


        if not trade:

            return False



        entry = float(
            trade["entry"]
        )

        quantity = float(
            trade["quantity"]
        )

        side = trade["side"]



        if side == "LONG":

            pnl = (
                float(exit_price)
                -
                entry
            ) * quantity


        else:

            pnl = (
                entry
                -
                float(exit_price)
            ) * quantity



        execute_query(
            """
            UPDATE trades

            SET

                status='CLOSED',

                pnl=?,

                close_reason=?,

                closed_at=?

            WHERE id=?

            """,
            (
                pnl,
                reason,
                datetime.utcnow().isoformat(),
                trade["id"]
            )
        )



        logger.info(
            f"CLOSE TRADE {symbol} PNL={pnl}"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
