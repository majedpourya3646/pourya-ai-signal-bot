import json
import os
from datetime import datetime

FILE_NAME = "data/history.json"


def load_trades():

    if not os.path.exists(FILE_NAME):
        return []

    try:

        with open(FILE_NAME, "r") as f:
            return json.load(f)

    except Exception:
        return []


def save_trades(data):

    os.makedirs("data", exist_ok=True)

    with open(FILE_NAME, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )


def add_trade(
    symbol,
    signal,
    entry,
    tp,
    sl,
    result=None,
    profit=0,
    quantity=0,
    confidence=0,
    grade=""
):

    trades = load_trades()

    trades.append({

        "symbol": symbol,

        "signal": signal,

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "quantity": quantity,

        "confidence": confidence,

        "grade": grade,

        "result": result,

        "profit": profit,

        "open_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "close_time": None

    })

    save_trades(trades)


def update_trade(
    symbol,
    result,
    profit
):

    trades = load_trades()

    for trade in reversed(trades):

        if (
            trade["symbol"] == symbol
            and
            trade["result"] is None
        ):

            trade["result"] = result

            trade["profit"] = round(
                profit,
                2
            )

            trade["close_time"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            break

    save_trades(trades)


def statistics():

    trades = load_trades()

    total = len(trades)

    wins = len([
        t for t in trades
        if t["result"] == "WIN"
    ])

    losses = len([
        t for t in trades
        if t["result"] == "LOSS"
    ])

    open_trades = len([
        t for t in trades
        if t["result"] is None
    ])

    total_profit = round(
        sum(
            t.get("profit", 0)
            for t in trades
        ),
        2
    )

    closed = wins + losses

    win_rate = round(
        (wins / closed) * 100,
        2
    ) if closed else 0

    avg_profit = round(
        total_profit / closed,
        2
    ) if closed else 0

    best_trade = max(
        [t.get("profit", 0) for t in trades],
        default=0
    )

    worst_trade = min(
        [t.get("profit", 0) for t in trades],
        default=0
    )

    return {

        "total": total,

        "open": open_trades,

        "wins": wins,

        "losses": losses,

        "closed": closed,

        "win_rate": win_rate,

        "profit": total_profit,

        "average_profit": avg_profit,

        "best_trade": round(best_trade, 2),

        "worst_trade": round(worst_trade, 2)

    }


def report():

    stats = statistics()

    return (

        "🤖 Pourya Trader AI\n\n"

        "📊 گزارش عملکرد\n\n"

        f"📈 کل معاملات: {stats['total']}\n"

        f"🟢 باز: {stats['open']}\n"

        f"🏁 بسته شده: {stats['closed']}\n\n"

        f"✅ موفق: {stats['wins']}\n"

        f"❌ ناموفق: {stats['losses']}\n\n"

        f"🎯 Win Rate: {stats['win_rate']}%\n"

        f"💰 سود/ضرر کل: {stats['profit']}%\n"

        f"📊 میانگین هر معامله: {stats['average_profit']}%\n"

        f"🥇 بهترین معامله: {stats['best_trade']}%\n"

        f"📉 بدترین معامله: {stats['worst_trade']}%\n\n"

        "🚀 AI Trading System"

    )
