
import json
import os
from datetime import datetime, timezone

from risk_manager import (
    can_open_trade,
    validate_trade
)


TRADE_FILE = "data/open_trades.json"



def now():

    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )



def load_trades():

    if not os.path.exists(TRADE_FILE):
        return {}

    try:
        with open(
            TRADE_FILE,
            "r"
        ) as f:
            return json.load(f)

    except Exception:
        return {}



def save_trades(trades):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        TRADE_FILE,
        "w"
    ) as f:

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


    # جلوگیری از خرید تکراری
    if symbol in trades:
        return False



    # محدودیت تعداد معاملات
    if not can_open_trade(trades):
        return False



    if all(
        x is not None
        for x in [
            balance,
            start_balance,
            entry,
            tp,
            sl
        ]
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
    order_id=None,
    side="LONG",
    leverage=1
):
    print("OPEN TRADE CALLED:", symbol)
    trades = load_trades()


    trades[symbol] = {

        "symbol": symbol,

        "side": side,

        "entry": float(entry),

        "tp": float(tp),

        "sl": float(sl),

        "quantity": float(quantity),

        "leverage": leverage,

        "signal": signal,

        "confidence": confidence,

        "grade": grade,

        "order_id": order_id,

        "status": "OPEN",

        "open_time": now(),

        "updated_at": now()

    }


    save_trades(trades)



def close_trade(symbol):

    trades = load_trades()


    if symbol in trades:

        del trades[symbol]


    save_trades(trades)



def update_trade(
    symbol,
    **kwargs
):

    trades = load_trades()


    if symbol in trades:

        for key,value in kwargs.items():

            trades[symbol][key] = value


        trades[symbol]["updated_at"] = now()


        save_trades(trades)



def update_stop_loss(
    symbol,
    new_sl
):

    update_trade(
        symbol,
        sl=new_sl
    )



def update_take_profit(
    symbol,
    new_tp
):

    update_trade(
        symbol,
        tp=new_tp
    )



def trade_exists(symbol):

    return symbol in load_trades()



def get_trade(symbol):

    return load_trades().get(symbol)



def get_all_trades():

    return load_trades()



def count_open_trades():

    trades = load_trades()

    return len(trades)



def clear_all_trades():

    save_trades({})
