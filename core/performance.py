# core/performance.py

import json
import os

from core.logger import logger



PERFORMANCE_FILE = "data/performance.json"



DEFAULT_DATA = {

    "wins": 0,

    "losses": 0,

    "total_profit": 0,

    "total_loss": 0

}



def load_performance():

    try:


        if not os.path.exists(
            PERFORMANCE_FILE
        ):


            save_performance(
                DEFAULT_DATA
            )


            return DEFAULT_DATA



        with open(

            PERFORMANCE_FILE,

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


        return DEFAULT_DATA




def save_performance(
    data
):

    try:


        os.makedirs(

            "data",

            exist_ok=True

        )


        with open(

            PERFORMANCE_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                data,

                file,

                ensure_ascii=False,

                indent=4

            )



    except Exception as e:


        logger.exception(
            e
        )




def add_trade_result(
    profit
):

    try:


        data = load_performance()



        if profit > 0:


            data["wins"] += 1

            data["total_profit"] += profit



        else:


            data["losses"] += 1

            data["total_loss"] += abs(
                profit
            )



        save_performance(
            data
        )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def get_summary():

    data = load_performance()



    total = (

        data.get("wins",0)

        +

        data.get("losses",0)

    )



    win_rate = 0



    if total > 0:


        win_rate = round(

            (

                data.get("wins",0)

                /

                total

            )

            *

            100,

            2

        )



    return {

        "wins": data.get(
            "wins",
            0
        ),

        "losses": data.get(
            "losses",
            0
        ),

        "win_rate": win_rate,

        "profit": data.get(
            "total_profit",
            0
        ),

        "loss": data.get(
            "total_loss",
            0
        )

    }




def get_daily_performance():

    return get_summary()
