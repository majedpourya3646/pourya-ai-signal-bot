import json
import os

FILE = "trades.json"


def load_trades():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save_trades(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def can_buy(symbol):
    trades = load_trades()
    return symbol not in trades


def open_trade(symbol, entry, tp, sl):
    trades = load_trades()

    trades[symbol] = {
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "status": "OPEN"
    }

    save_trades(trades)


def close_trade(symbol):
    trades = load_trades()

    if symbol in trades:
        del trades[symbol]

    save_trades(trades)
