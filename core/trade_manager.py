# core/trade_manager.py

from __future__ import annotations

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
                ticket,
                symbol,
                side,
                entry,
                exit_price,
                tp,
                sl,
                quantity,
                confidence,
                pnl,
                status,
                opened_at,
                closed_at
            )
            VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ticket,
                symbol,
                side,
                float(entry),
                None,
                float(tp),
                float(sl),
                float(quantity),
                float(confidence),
                0.0,
                "OPEN",
                datetime.utcnow().isoformat(),
                None
            )
        )

        trade_id = cursor.lastrowid

        conn.commit()

        conn.close()

        logger.info(
            f"TRADE OPENED "
            f"ID={trade_id} "
            f"TICKET={ticket} "
            f"{symbol} "
            f"{side}"
        )

        return trade_id

    except Exception as exc:

        logger.exception(
            f"OPEN TRADE ERROR {exc}"
        )

        return None


# ===========================
# Save Trade
# ===========================

def save_trade(trade):

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

        return open_trade(
            symbol=symbol,
            side=side,
            entry=entry,
            tp=tp,
            sl=sl,
            quantity=quantity,
            confidence=confidence,
            ticket=ticket
        )

    except Exception as exc:

        logger.exception(
            f"SAVE TRADE ERROR {exc}"
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

        cursor.execute(
            """
            UPDATE trades
            SET
                status=?,
                pnl=COALESCE(?, pnl),
                exit_price=COALESCE(?, exit_price),
                closed_at=?
            WHERE id=?
            """,
            (
                status,
                float(pnl) if pnl is not None else None,
                float(exit_price) if exit_price is not None else None,
                datetime.utcnow().isoformat()
                if status.upper() in ("CLOSED", "CLOSE", "TP", "SL")
                else None,
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

    except Exception as exc:

        logger.exception(
            f"UPDATE TRADE STATUS ERROR {exc}"
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
                exit_price=?,
                pnl=?,
                closed_at=?
            WHERE id=?
            """,
            (
                "CLOSED",
                float(exit_price),
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
            f"EXIT={exit_price} "
            f"PNL={pnl}"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"CLOSE TRADE ERROR {exc}"
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

    except Exception as exc:

        logger.exception(
            f"GET OPEN TRADES ERROR {exc}"
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

    except Exception as exc:

        logger.exception(
            f"GET TRADE HISTORY ERROR {exc}"
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

    except Exception as exc:

        logger.exception(
            f"GET TRADE ERROR {exc}"
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
            return int(result[0])

        return 0

    except Exception as exc:

        logger.exception(
            f"COUNT OPEN TRADES ERROR {exc}"
        )

        return 0


__all__ = [
    "open_trade",
    "save_trade",
    "update_trade_status",
    "close_trade",
    "get_open_trades",
    "get_trade_history",
    "get_trade_by_id",
    "count_open_trades",
]
