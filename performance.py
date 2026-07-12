import json
import os

FILE_NAME = "trades.json"


def load_trades():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []


def save_trades(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)


def add_trade(symbol, signal, entry, tp, sl, result=None):

    trades = load_trades()

    trades.append({
        "symbol": symbol,
        "signal": signal,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "result": result
    })

    save_trades(trades)


def statistics():

    trades = load_trades()

    total = len(trades)

    wins = len([x for x in trades if x["result"] == "WIN"])

    losses = len([x for x in trades if x["result"] == "LOSS"])

    if total == 0:
        win_rate = 0
    else:
        win_rate = round((wins / total) * 100, 2)

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate
    }
