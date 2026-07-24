# core/trade_history.py

import json
import os

from datetime import datetime

from core.logger import logger



TRADES_FILE = "data/trades.json"



def load_trades():

    try:


        if not os.path.exists(
            TRADES_FILE
        ):


            save_trades([])


            return []



        with open(

            TRADES_FILE,

            "r",

            encoding="utf-8"

        ) as file:


            return json.load(
                file
            )



    except Exception as e:


        logger.exception(
            e
        )


        return []




def save_trades(
    trades
):

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        with open(

            TRADES_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                trades,

                file,

                ensure_ascii=False,

                indent=4

            )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def add_trade_history(
    trade
):

    try:


        trades = load_trades()



        trade["created_at"] = (

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

        )



        trades.append(
            trade
        )



        save_trades(
            trades
        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def close_trade_history(
    symbol,
    pnl
):

    try:


        trades = load_trades()



        for trade in reversed(
            trades
        ):


            if (

                trade.get(
                    "symbol"
                ) == symbol

                and

                trade.get(
                    "status",
                    "OPEN"
                ) == "OPEN"

            ):


                trade["status"] = "CLOSED"

                trade["pnl"] = pnl

                trade["closed_at"] = (

                    datetime.now().strftime(

                        "%Y-%m-%d %H:%M:%S"

                    )

                )

                break



        save_trades(
            trades
        )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def get_trade_history(
    limit=50
):

    trades = load_trades()



    return trades[-limit:]




def get_total_profit():

    try:


        trades = load_trades()



        total = 0



        for trade in trades:


            total += float(

                trade.get(
                    "pnl",
                    0
                )

            )



        return round(
            total,
            2
        )



    except Exception as e:


        logger.exception(
            e
        )


        return 0
