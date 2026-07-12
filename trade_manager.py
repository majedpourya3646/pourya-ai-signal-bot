import json
import os
from datetime import datetime

from risk_manager import can_open_trade


TRADE_FILE = "open_trades.json"


MAX_TRADES = 3



def load_trades():

    if os.path.exists(TRADE_FILE):

        with open(TRADE_FILE, "r") as f:

            return json.load(f)

    return {}



def save_trades(trades):

    with open(TRADE_FILE, "w") as f:

        json.dump(
            trades,
            f,
            indent=4
        )



def can_buy(symbol):

    trades = load_trades()


    # جلوگیری از خرید تکراری همان ارز

    if symbol in trades:

        return False



    # محدودیت تعداد معاملات

    if not can_open_trade(trades):

        return False


    return True




def open_trade(
        symbol,
        entry,
        tp,
        sl,
        quantity=0
):

    trades = load_trades()



    trades[symbol] = {

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "quantity": quantity,

        "open_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

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
