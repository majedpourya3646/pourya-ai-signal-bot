import os
import json
from datetime import datetime

from config import (
    MAX_OPEN_TRADES,
    DEFAULT_TP,
    DEFAULT_SL,
)

from core.logger import logger


TRADES_FILE = "data/open_trades.json"


# =========================
# Load Trades
# =========================

def load_trades():

    if not os.path.exists(TRADES_FILE):
        return {}

    try:
        with open(
            TRADES_FILE,
            "r"
        ) as f:

            return json.load(f)

    except Exception:

        return {}



# =========================
# Save Trades
# =========================

def save_trades(trades):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        TRADES_FILE,
        "w"
    ) as f:

        json.dump(
            trades,
            f,
            indent=4
        )



# =========================
# Current Trades
# =========================

def get_all_trades():

    trades = load_trades()

    print(
        "CURRENT TRADES:"
    )

    print(
        trades
    )

    return trades



# =========================
# Check Capacity
# =========================

def can_buy(symbol):

    trades = load_trades()


    if symbol in trades:

        return False


    if len(trades) >= MAX_OPEN_TRADES:

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
    confidence=0,
    signal="BUY",
    leverage=1,
    order_id=None
):


    trades = load_trades()


    # TP / SL
    tp = entry * (
        1 + DEFAULT_TP / 100
    )


    sl = entry * (
        1 - DEFAULT_SL / 100
    )



    trade = {

        "symbol": symbol,

        "side": side,

        "entry": entry,

        "tp": round(tp, 8),

        "sl": round(sl, 8),

        "quantity": quantity,

        "leverage": leverage,

        "signal": signal,

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


    logger.info(
        f"OPEN TRADE CALLED: {symbol}"
    )


    print(
        "SAVED TRADES:",
        trades
    )


    print(
        "FILE PATH:",
        os.path.abspath(TRADES_FILE)
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
