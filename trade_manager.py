
import sqlite3
import os

from datetime import datetime

from config import (
    MAX_OPEN_TRADES,
    DEFAULT_TP,
    DEFAULT_SL,
    LEVERAGE
)


DB_FILE = "data/trades.db"


# =====================================
# Database
# =====================================

def get_connection():

    os.makedirs(
        "data",
        exist_ok=True
    )

    return sqlite3.connect(DB_FILE)


def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT UNIQUE,

            side TEXT,

            entry REAL,

            tp REAL,

            sl REAL,

            quantity REAL,

            leverage INTEGER,

            signal TEXT,

            confidence INTEGER,

            order_id TEXT,

            status TEXT,

            open_time TEXT,

            updated_at TEXT,

            exit_price REAL,

            profit REAL,

            profit_percent REAL,

            close_reason TEXT,

            close_time TEXT

        )
        """
    )

    conn.commit()

    conn.close()


init_db()


# =====================================
# Helpers
# =====================================

def now():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =====================================
# Get Trades
# =====================================

def get_all_trades():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *

        FROM trades

        WHERE status='OPEN'
        """
    )

    rows = cursor.fetchall()

    conn.close()

    trades = {}

    for row in rows:

        trades[row[1]] = {

            "symbol": row[1],

            "side": row[2],

            "entry": row[3],

            "tp": row[4],

            "sl": row[5],

            "quantity": row[6],

            "leverage": row[7],

            "signal": row[8],

            "confidence": row[9],

            "order_id": row[10],

            "status": row[11],

            "open_time": row[12],

            "updated_at": row[13]

        }

    return trades


# =====================================
# Permission
# =====================================

def can_buy(symbol):

    trades = get_all_trades()

    if symbol in trades:

        print(
            f"SKIP {symbol}: already open"
        )

        return False

    if len(trades) >= MAX_OPEN_TRADES:

        print(
            "MAX OPEN TRADES REACHED"
        )

        return False

    return True

def open_trade(
    symbol,
    side,
    entry,
    quantity,
    confidence,
    signal="BUY",
    order_id=None
):

    if not can_buy(symbol):
        return False

    if side.upper() in ("BUY", "STRONG BUY", "LONG"):

        position = "LONG"

        tp = round(
            entry * (1 + DEFAULT_TP / 100),
            8
        )

        sl = round(
            entry * (1 - DEFAULT_SL / 100),
            8
        )

    else:

        position = "SHORT"

        tp = round(
            entry * (1 - DEFAULT_TP / 100),
            8
        )

        sl = round(
            entry * (1 + DEFAULT_SL / 100),
            8
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO trades
        (
            symbol,
            side,
            entry,
            tp,
            sl,
            quantity,
            leverage,
            signal,
            confidence,
            order_id,
            status,
            open_time,
            updated_at
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            symbol,
            position,
            entry,
            tp,
            sl,
            quantity,
            LEVERAGE if not PAPER_TRADING else 1,
            signal,
            confidence,
            order_id,
            "OPEN",
            now(),
            now()
        )
    )

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success

def close_trade(
    symbol,
    exit_price,
    reason="MANUAL"
):

    trades = get_all_trades()

    if symbol not in trades:
        return False

    trade = trades[symbol]

    entry = float(trade["entry"])
    quantity = float(trade["quantity"])
    side = trade["side"]

    if side == "LONG":

        profit = (
            exit_price - entry
        ) * quantity

        profit_percent = (
            (exit_price - entry)
            / entry
        ) * 100

    else:

        profit = (
            entry - exit_price
        ) * quantity

        profit_percent = (
            (entry - exit_price)
            / entry
        ) * 100

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE trades
        SET
            status=?,
            exit_price=?,
            profit=?,
            profit_percent=?,
            close_reason=?,
            close_time=?,
            updated_at=?
        WHERE symbol=?
        AND status='OPEN'
        """,
        (
            "CLOSED",
            round(exit_price, 8),
            round(profit, 8),
            round(profit_percent, 2),
            reason,
            now(),
            now(),
            symbol
        )
    )

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated
