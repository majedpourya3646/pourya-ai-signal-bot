from datetime import datetime

from core.logger import logger

from core.database_manager import (
    get_connection
)


# ===========================
# Open Trade
# ===========================

def open_trade(
    symbol,
    side,
    entry,
    tp,
    sl,
    quantity,
    confidence,
    ticket=None
):

    try:

        conn = get_connection()

        if conn is None:

            logger.error(
                "DATABASE CONNECTION FAILED"
            )

            return None

        cursor = conn.cursor()

        cursor.execute(
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
                status,
                opened_at
            )
            VALUES
            (?,?,?,?,?,?,?,?,?)
            """,
            (
                symbol,
                side,
                float(entry),
                float(tp),
                float(sl),
                float(quantity),
                float(confidence),
                "OPEN",
                datetime.utcnow().isoformat()
            )
        )

        trade_id = cursor.lastrowid

        conn.commit()

        conn.close()

        logger.info(
            f"TRADE OPENED "
            f"ID={trade_id} "
            f"{symbol} "
            f"{side}"
        )

        return trade_id

    except Exception as e:

        logger.exception(
            f"OPEN TRADE ERROR {e}"
        )

        return None


# ===========================
# Save Trade
# ===========================

def save_trade(
    trade
):

    try:

        if not trade:

            return None

        symbol = trade.get(
            "symbol"
        )

        side = trade.get(
            "side"
        )

        entry = trade.get(
            "entry",
            0
        )

        tp = trade.get(
            "tp",
            0
        )

        sl = trade.get(
            "sl",
            0
        )

        quantity = trade.get(
            "quantity",
            trade.get(
                "volume",
                0
            )
        )

        confidence = trade.get(
            "confidence",
            0
        )

        ticket = trade.get(
            "ticket"
        )

        trade_id = open_trade(
            symbol=symbol,
            side=side,
            entry=entry,
            tp=tp,
            sl=sl,
            quantity=quantity,
            confidence=confidence,
            ticket=ticket
        )

        if trade_id is None:

            return None

        logger.info(
            f"TRADE SAVED "
            f"ID={trade_id} "
            f"{symbol}"
        )

        return trade_id

    except Exception as e:

        logger.exception(
            f"SAVE TRADE ERROR {e}"
        )

        return None


# ===========================
# Update Trade Status
# ===========================

def update_trade_status(
    trade_id,
    status,
    pnl=None,
    exit_price=None
):

    try:

        conn = get_connection()

        if conn is None:

            return False

        cursor = conn.cursor()

        if pnl is not None:

            cursor.execute(
                """
                UPDATE trades
                SET
                    status=?,
                    pnl=?,
                    closed_at=?
                WHERE id=?
                """,
                (
                    status,
                    float(pnl),
                    datetime.utcnow().isoformat(),
                    trade_id
                )
            )

        else:

            cursor.execute(
                """
                UPDATE trades
                SET
                    status=?
                WHERE id=?
                """,
                (
                    status,
                    trade_id
                )
            )

        conn.commit()

        affected = cursor.rowcount

        conn.close()

        if affected == 0:

            logger.warning(
                f"TRADE NOT FOUND ID={trade_id}"
            )

            return False

        logger.info(
            f"TRADE STATUS UPDATED "
            f"ID={trade_id} "
            f"STATUS={status}"
        )

        return True

    except Exception as e:

        logger.exception(
            f"UPDATE TRADE STATUS ERROR {e}"
        )

        return False


# ===========================
# Close Trade
# ===========================

def close_trade(
    trade_id,
    exit_price,
    pnl
):

    try:

        conn = get_connection()

        if conn is None:

            return False

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE trades
            SET
                status=?,
                pnl=?,
                closed_at=?
            WHERE id=?
            """,
            (
                "CLOSED",
                float(pnl),
                datetime.utcnow().isoformat(),
                trade_id
            )
        )

        conn.commit()

        affected = cursor.rowcount

        conn.close()

        if affected == 0:

            logger.warning(
                f"TRADE NOT FOUND ID={trade_id}"
            )

            return False

        logger.info(
            f"TRADE CLOSED "
            f"ID={trade_id} "
            f"PNL={pnl}"
        )

        return True

    except Exception as e:

        logger.exception(
            f"CLOSE TRADE ERROR {e}"
        )

        return False


# ===========================
# Get Open Trades
# ===========================

def get_open_trades():

    try:

        conn = get_connection()

        if conn is None:

            return []

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM trades
            WHERE status='OPEN'
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        conn.close()

        return [
            dict(row)
            for row in rows
        ]

    except Exception as e:

        logger.exception(
            f"GET OPEN TRADES ERROR {e}"
        )

        return []


# ===========================
# Get Trade History
# ===========================

def get_trade_history(
    limit=100
):

    try:

        conn = get_connection()

        if conn is None:

            return []

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM trades
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                int(limit),
            )
        )

        rows = cursor.fetchall()

        conn.close()

        return [
            dict(row)
            for row in rows
        ]

    except Exception as e:

        logger.exception(
            f"GET TRADE HISTORY ERROR {e}"
        )

        return []


# ===========================
# Get Trade By ID
# ===========================

def get_trade_by_id(
    trade_id
):

    try:

        conn = get_connection()

        if conn is None:

            return None

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM trades
            WHERE id=?
            """,
            (
                trade_id,
            )
        )

        row = cursor.fetchone()

        conn.close()

        if row:

            return dict(row)

        return None

    except Exception as e:

        logger.exception(
            f"GET TRADE ERROR {e}"
        )

        return None


# ===========================
# Count Open Trades
# ===========================

def count_open_trades():

    try:

        conn = get_connection()

        if conn is None:

            return 0

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM trades
            WHERE status='OPEN'
            """
        )

        result = cursor.fetchone()

        conn.close()

        if result:

            return int(
                result[0]
            )

        return 0

    except Exception as e:

        logger.exception(
            f"COUNT OPEN TRADES ERROR {e}"
        )

        return 0
