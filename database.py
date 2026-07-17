import sqlite3
import os
from datetime import datetime


DB_FOLDER = "data"
DB_FILE = os.path.join(
    DB_FOLDER,
    "trader.db"
)


def get_connection():

    os.makedirs(
        DB_FOLDER,
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.row_factory = sqlite3.Row

    return conn



def init_database():

    conn = get_connection()

    cursor = conn.cursor()


    # معاملات باز
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS open_trades (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT UNIQUE,

        side TEXT,

        entry REAL,

        tp REAL,

        sl REAL,

        quantity REAL,

        leverage INTEGER,

        confidence INTEGER,

        signal TEXT,

        order_id TEXT,

        status TEXT,

        open_time TEXT

    )
    """)



    # تاریخچه معاملات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        result TEXT,

        profit REAL,

        close_time TEXT

    )
    """)



    conn.commit()

    conn.close()



def add_open_trade(trade):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""

    INSERT OR REPLACE INTO open_trades

    (
    symbol,
    side,
    entry,
    tp,
    sl,
    quantity,
    leverage,
    confidence,
    signal,
    order_id,
    status,
    open_time
    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    trade["symbol"],
    trade["side"],
    trade["entry"],
    trade["tp"],
    trade["sl"],
    trade["quantity"],
    trade["leverage"],
    trade["confidence"],
    trade["signal"],
    trade["order_id"],
    trade["status"],
    trade["open_time"]

    ))


    conn.commit()

    conn.close()



def get_open_trades():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT * FROM open_trades
        WHERE status='OPEN'
        """
    )


    rows = cursor.fetchall()

    conn.close()


    return [
        dict(row)
        for row in rows
    ]



def close_trade_db(
    symbol,
    result,
    profit
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
    """
    UPDATE open_trades

    SET status='CLOSED'

    WHERE symbol=?

    """,
    (symbol,)
    )


    cursor.execute(
    """
    INSERT INTO history

    (
    symbol,
    result,
    profit,
    close_time
    )

    VALUES (?,?,?,?)

    """,

    (
    symbol,
    result,
    profit,
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    ))


    conn.commit()

    conn.close()
