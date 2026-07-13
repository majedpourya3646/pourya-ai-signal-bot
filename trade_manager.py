import json
import os
from datetime import datetime

from risk_manager import (
    can_open_trade,
    validate_trade
)

TRADE_FILE = "data/open_trades.json"


def load_trades():

    if not os.path.exists(TRADE_FILE):
        return {}

    try:
        with open(TRADE_FILE, "r") as f:
            return json.load(f)

    except Exception:
        return {}


def save_trades(trades):

    os.makedirs("data", exist_ok=True)

    with open(TRADE_FILE, "w") as f:
        json.dump(
            trades,
            f,
            indent=4
        )


def can_buy(
    symbol,
    balance=None,
    start_balance=None,
    entry=None,
    tp=None,
    sl=None
):

    trades = load_trades()

    if symbol in trades:
        return False

    if not can_open_trade(trades):
        return False

    if (
        balance is not None
        and
        start_balance is not None
        and
        entry is not None
        and
        tp is not None
        and
        sl is not None
    ):

        valid, _ = validate_trade(
            balance,
            start_balance,
            trades,
            entry,
            tp,
            sl
        )

        if not valid:
            return False

    return True


def open_trade(
    symbol,
    entry,
    tp,
    sl,
    quantity=0,
    signal="",
    confidence=0,
    grade="",
    order_id=None
):

    trades = load_trades()

    trades[symbol] = {

        "symbol": symbol,

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "quantity": quantity,

        "signal": signal,

        "confidence": confidence,

        "grade": grade,

        "order_id": order_id,

        "status": "OPEN",

        "open_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    save_trades(trades)


def close_trade(symbol):

    trades = load_trades()

    if symbol in trades:

        trades[symbol]["status"] = "CLOSED"

        trades[symbol]["close_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        del trades[symbol]

    save_trades(trades)


def update_stop_loss(
    symbol,
    new_sl
):

    trades = load_trades()

    if symbol in trades:

        trades[symbol]["sl"] = new_sl

        save_trades(trades)


def update_take_profit(
    symbol,
    new_tp
):

    trades = load_trades()

    if symbol in trades:

        trades[symbol]["tp"] = new_tp

        save_trades(trades)


def trade_exists(symbol):

    trades = load_trades()

    return symbol in trades


def get_trade(symbol):

    trades = load_trades()

    return trades.get(symbol)


def get_all_trades():

    return load_trades()


def count_open_trades():

    return len(load_trades())


def clear_all_trades():

    save_trades({})
