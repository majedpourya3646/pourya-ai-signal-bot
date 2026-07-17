import sqlite3
from datetime import datetime

from config import (
    MAX_OPEN_TRADES,
    DEFAULT_TP,
    DEFAULT_SL,
    LEVERAGE
)


DB_FILE = "data/trades.db"



# ==========================
# Database
# ==========================

def get_connection():

    import os

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

            symbol TEXT,

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



# ==========================
# Get Trades
# ==========================

def get_all_trades():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
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

        FROM trades

        WHERE status='OPEN'
        """
    )


    rows = cursor.fetchall()


    conn.close()



    trades = {}


    for r in rows:

        trades[r[0]] = {

            "symbol": r[0],

            "side": r[1],

            "entry": r[2],

            "tp": r[3],

            "sl": r[4],

            "quantity": r[5],

            "leverage": r[6],

            "signal": r[7],

            "confidence": r[8],

            "order_id": r[9],

            "status": r[10],

            "open_time": r[11],

            "updated_at": r[12]

        }


    return trades




# ==========================
# Permission
# ==========================

def can_buy(symbol=None):


    trades = get_all_trades()



    if symbol and symbol in trades:

        return False



    if len(trades) >= MAX_OPEN_TRADES:

        return False



    return True





# ==========================
# Open Trade
# ==========================

def open_trade(
        symbol,
        side,
        entry,
        quantity,
        confidence,
        signal="BUY",
        order_id=None
):


    conn = get_connection()

    cursor = conn.cursor()



    tp = entry * (
        1 + DEFAULT_TP / 100
    )


    sl = entry * (
        1 - DEFAULT_SL / 100
    )



    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )



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

        "LONG" if side.lower()=="buy" else "SHORT",

        entry,

        round(tp,8),

        round(sl,8),

        quantity,

        LEVERAGE,

        signal,

        confidence,

        order_id,

        "OPEN",

        now,

        now

        )

    )



    conn.commit()

    conn.close()



    return True





# ==========================
# Close Trade
# ==========================

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

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        symbol

        )

    )



    conn.commit()

    changed = cursor.rowcount


    conn.close()



    return changed > 0
