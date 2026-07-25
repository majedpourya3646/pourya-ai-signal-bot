from core.database_manager import execute_query
from core.logger import logger


def can_buy(symbol):

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
    tp=0,
    sl=0,
    order_id=None
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
            (
                ?,?,?,?,?,?,?,?
            )
            """,
            (
                symbol,
                side,
                float(entry),
                float(tp),
                float(sl),
                float(quantity),
                float(confidence),
                "OPEN"
            )
        )

        logger.info(
            f"TRADE OPENED {symbol}"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False


def get_trade(symbol):

    try:

        result = execute_query(
            """
            SELECT
                id,
                symbol,
                side,
                entry,
                tp,
                sl,
                quantity,
                confidence,
                status,
                pnl
            FROM trades
            WHERE symbol=?
            AND status='OPEN'
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

            "id": row[0],
            "symbol": row[1],
            "side": row[2],
            "entry": row[3],
            "tp": row[4],
            "sl": row[5],
            "quantity": row[6],
            "confidence": row[7],
            "status": row[8],
            "pnl": row[9]

        }

    except Exception as e:

        logger.exception(e)

        return None


def get_open_trades():

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
                confidence
            FROM trades
            WHERE status='OPEN'
            """
        )

        trades = []

        for row in result:

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
                pnl,
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
    reason=""
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

        qty = float(
            trade["quantity"]
        )

        side = trade["side"]

        if side == "LONG":

            pnl = (
                exit_price - entry
            ) * qty

        else:

            pnl = (
                entry - exit_price
            ) * qty

        execute_query(
            """
            UPDATE trades
            SET
                status='CLOSED',
                pnl=?
            WHERE id=?
            """,
            (
                pnl,
                trade["id"]
            )
        )

        logger.info(
            f"{symbol} CLOSED | {reason} | PNL={pnl}"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False
