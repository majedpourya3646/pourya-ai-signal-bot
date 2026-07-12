import json
import os


FILE = "paper_trades.json"


def load_trades():

    if os.path.exists(FILE):

        with open(FILE, "r") as f:
            return json.load(f)

    return {}



def save_trades(data):

    with open(FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=4
        )



def open_paper_trade(
    symbol,
    entry,
    tp,
    sl
):

    trades = load_trades()


    trades[symbol] = {

        "entry": entry,

        "tp": tp,

        "sl": sl,

        "status": "OPEN"

    }


    save_trades(trades)



def check_paper_trades(
    symbol,
    high,
    low
):

    trades = load_trades()


    if symbol not in trades:

        return None



    trade = trades[symbol]



    if high >= trade["tp"]:

        trade["status"] = "WIN"

        save_trades(trades)

        return "WIN"



    if low <= trade["sl"]:

        trade["status"] = "LOSS"

        save_trades(trades)

        return "LOSS"



    return "OPEN"



def get_paper_trades():

    return load_trades()
