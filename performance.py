import json
import os

FILE_NAME = "history.json"


def load_trades():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []


def save_trades(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)


def add_trade(symbol, signal, entry, tp, sl, result=None, profit=0):

    trades = load_trades()

    trades.append({
        "symbol": symbol,
        "signal": signal,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "result": result,
        "profit": profit
    })

    save_trades(trades)


def update_trade(symbol, result, profit):

    trades = load_trades()

    for trade in reversed(trades):

        if trade["symbol"] == symbol and trade["result"] is None:

            trade["result"] = result
            trade["profit"] = round(profit, 2)
            break

    save_trades(trades)


def statistics():

    trades = load_trades()

    total = len(trades)

    wins = len([t for t in trades if t["result"] == "WIN"])
    losses = len([t for t in trades if t["result"] == "LOSS"])

    open_trades = len([t for t in trades if t["result"] is None])

    total_profit = round(sum(t.get("profit", 0) for t in trades), 2)

    if total == 0:
        win_rate = 0
    else:
        win_rate = round((wins / total) * 100, 2)

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "open": open_trades,
        "win_rate": win_rate,
        "profit": total_profit
    }


def report():

    stats = statistics()

    message = (
        "📊 گزارش عملکرد ربات\n\n"
        f"📈 کل معاملات: {stats['total']}\n"
        f"🟢 معاملات باز: {stats['open']}\n"
        f"✅ معاملات موفق: {stats['wins']}\n"
        f"❌ معاملات ناموفق: {stats['losses']}\n\n"
        f"🎯 درصد موفقیت: {stats['win_rate']}٪\n"
        f"💰 سود کل: {stats['profit']}٪\n\n"
        "🤖 Pourya Trader AI"
    )

    return message
