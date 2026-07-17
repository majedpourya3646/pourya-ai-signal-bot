import os
import json
from datetime import datetime

from config import (
    MAX_OPEN_TRADES,
    DEFAULT_TP,
    DEFAULT_SL,
)

from core.logger import logger


# =========================
# File
# =========================

DATA_DIR = "data"

FILE_PATH = os.path.join(
    DATA_DIR,
    "open_trades.json"
)


if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)



# =========================
# Load Trades
# =========================

def load_trades():

    if not os.path.exists(FILE_PATH):
        return {}

    try:
        with open(
            FILE_PATH,
            "r"
        ) as f:

            return json.load(f)

    except Exception:

        return {}



# =========================
# Save Trades
# =========================

def save_trades(trades):

    with open(
        FILE_PATH,
        "w"
    ) as f:

        json.dump(
            trades,
            f,
            indent=4
        )



# =========================
# Get Trades
# =========================

def get_all_trades():

    return load_trades()



# =========================
# Check Permission
# =========================

def can_buy(
    symbol,
    side,
    confidence,
    quantity,
    tp,
    sl
):

    trades = load_trades()


    print(
        "CURRENT TRADES:"
    )

    print(
        trades
    )


    # جلوگیری از خرید تکراری

    if symbol in trades:

        logger.info(
            f"{symbol} already opened"
        )

        return False



    # محدودیت تعداد معاملات

    if len(trades) >= MAX_OPEN_TRADES:

        logger.info(
            "MAX OPEN TRADES REACHED"
        )

        return False



    return True



# =========================
# Open Trade
# =========================

def open_trade(
    symbol,
    side,
    entry,
    quantity,
    confidence,
    order_id=None
):


    trades = load_trades()



    if side.upper() == "LONG":

        tp = entry * (
            1 + DEFAULT_TP / 100
        )

        sl = entry * (
            1 - DEFAULT_SL / 100
        )

    else:

        tp = entry * (
            1 - DEFAULT_TP / 100
        )

        sl = entry * (
            1 + DEFAULT_SL / 100
        )



    trade = {

        "symbol": symbol,

        "side": side,

        "entry": entry,

        "tp": round(tp, 6),

        "sl": round(sl, 6),

        "quantity": quantity,

        "leverage": 10,

        "signal": "BUY",

        "confidence": confidence,

        "order_id": order_id,

        "status": "OPEN",

        "open_time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "updated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    }



    trades[symbol] = trade


    save_trades(
        trades
    )


    print(
        "SAVED TRADES:",
        trades
    )


    print(
        "FILE PATH:",
        FILE_PATH
    )


    return trade



# =========================
# Close Trade
# =========================

def close_trade(symbol):

    trades = load_trades()


    if symbol in trades:

        trades[symbol]["status"] = "CLOSED"

        trades[symbol]["updated_at"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )


        save_trades(
            trades
        )


        return True


    return False



# =========================
# Open Count
# =========================

def get_open_count():

    trades = load_trades()

    return len(trades)
