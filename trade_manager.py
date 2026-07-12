import json
import os

TRADE_FILE = "trades.json"


def load_trades():
    if os.path.exists(TRADE_FILE):
        with open(TRADE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_trades(trades):
    with open(TRADE_FILE, "w") as f:
        json.dump(trades, f, indent=4)


def can_buy(symbol):
    trades = load_trades()
    return symbol not in trades


def open_trade(symbol, entry, tp, sl):
    trades = load_trades()

    trades[symbol] = {
        "entry": entry,
        "tp": tp,
        "sl": sl
    }

    save_trades(trades)


def close_trade(symbol):
    trades = load_trades()

    if symbol in trades:
        del trades[symbol]

    save_trades(trades)


def get_trade(symbol):
    trades = load_trades()
    return trades.get(symbol)


def get_all_trades():
    return load_trades()
