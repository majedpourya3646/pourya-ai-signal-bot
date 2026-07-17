import sqlite3
from datetime import datetime
import os

from config import (
    MAX_OPEN_TRADES,
    DEFAULT_TP,
    DEFAULT_SL,
    LEVERAGE
)


DB_FILE = "data/trades.db"



def get_connection():

    os.makedirs(
        "data",
        exist_ok=True
    )

    return sqlite3.connect(
        DB_FILE
    )



def init_db():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (

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

            updated_at TEXT

        )
        """
    )


    conn.commit()
    conn.close()



init_db()



def now():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )



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


    for r in rows:

        trades[r[1]] = {

            "symbol": r[1],
            "side": r[2],
            "entry": r[3],
            "tp": r[4],
            "sl": r[5],
            "quantity": r[6],
            "leverage": r[7],
            "signal": r[8],
            "confidence": r[9],
            "order_id": r[10],
            "status": r[11],
            "open_time": r[12],
            "updated_at": r[13]

        }


    return trades



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



    tp = entry * (
        1 + DEFAULT_TP / 100
    )


    sl = entry * (
        1 - DEFAULT_SL / 100
    )


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT OR IGNORE INTO trades

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

        "LONG" if side.lower()=="buy"
        else "SHORT",

        entry,

        round(tp,8),

        round(sl,8),

        quantity,

        LEVERAGE,

        signal,

        confidence,

        order_id,

        "OPEN",

        now(),

        now()

        )

    )


    conn.commit()

    result = cursor.rowcount


    conn.close()


    if result:

        print(
            f"OPENED {symbol}"
        )

        return True


    print(
        f"FAILED OPEN {symbol}"
    )


    return False



def close_trade(symbol):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE trades

        SET

        status='CLOSED',

        updated_at=?

        WHERE symbol=?

        AND status='OPEN'

        """,

        (
            now(),
            symbol
        )

    )


    conn.commit()

    changed = cursor.rowcount

    conn.close()


    return changed > 0
