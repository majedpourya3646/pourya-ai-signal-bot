import json
import os
from datetime import datetime, timezone


FILE_NAME = "data/history.json"



def now():

    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )



def load_trades():

    if not os.path.exists(
        FILE_NAME
    ):
        return []


    try:

        with open(
            FILE_NAME,
            "r"
        ) as f:

            return json.load(f)


    except Exception:

        return []



def save_trades(
    data
):

    os.makedirs(
        "data",
        exist_ok=True
    )


    with open(
        FILE_NAME,
        "w"
    ) as f:

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
    grade="",
    side="LONG",
    leverage=1,
    order_id=None
):

    trades = load_trades()


    trades.append({

        "symbol": symbol,

        "side": side,

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "quantity": quantity,

        "leverage": leverage,

        "order_id": order_id,

        "signal": signal,

        "confidence": confidence,

        "grade": grade,

        "result": result,

        "profit": profit,

        "status": "OPEN",

        "open_time": now(),

        "close_time": None

    })


    save_trades(
        trades
    )



def update_trade(
    symbol,
    result,
    profit
):

    trades = load_trades()


    for trade in reversed(trades):

        if (
            trade["symbol"] == symbol
            and trade["status"] == "OPEN"
        ):

            trade["result"] = result

            trade["profit"] = round(
                profit,
                2
            )

            trade["status"] = "CLOSED"

            trade["close_time"] = now()

            break


    save_trades(
        trades
    )



def statistics():

    trades = load_trades()


    total = len(trades)


    wins = sum(
        1
        for t in trades
        if t.get("result") == "WIN"
    )


    losses = sum(
        1
        for t in trades
        if t.get("result") == "LOSS"
    )


    open_trades = sum(
        1
        for t in trades
        if t.get("status") == "OPEN"
    )


    closed = wins + losses


    total_profit = round(

        sum(
            t.get("profit",0)
            for t in trades
        ),

        2
    )


    avg_profit = round(

        total_profit / closed,

        2

    ) if closed else 0



    win_rate = round(

        (wins / closed) * 100,

        2

    ) if closed else 0



    profits = [

        t.get("profit",0)

        for t in trades

        if t.get("status") == "CLOSED"

    ]


    return {

        "total": total,

        "open": open_trades,

        "closed": closed,

        "wins": wins,

        "losses": losses,

        "win_rate": win_rate,

        "profit": total_profit,

        "average_profit": avg_profit,

        "best_trade": round(
            max(profits),
            2
        ) if profits else 0,

        "worst_trade": round(
            min(profits),
            2
        ) if profits else 0

    }



def report():

    s = statistics()


    return (

        "😎 <b>Pourya Trader AI</b>\n\n"

        "📊 <b>Performance Report</b>\n\n"

        f"📈 Total Trades : {s['total']}\n"

        f"🟢 Open : {s['open']}\n"

        f"🏁 Closed : {s['closed']}\n\n"

        f"✅ Wins : {s['wins']}\n"

        f"❌ Losses : {s['losses']}\n"

        f"🎯 Win Rate : {s['win_rate']}%\n\n"

        f"💰 Total Profit : {s['profit']}%\n"

        f"📊 Average : {s['average_profit']}%\n"

        f"🥇 Best : {s['best_trade']}%\n"

        f"📉 Worst : {s['worst_trade']}%\n\n"

        "🚀 AI Trading System"

    )
