# core/performance_tracker.py

import json
import os

from datetime import datetime

from core.logger import logger



PERFORMANCE_FILE = "data/performance.json"



def load_performance():

    try:

        if not os.path.exists(
            PERFORMANCE_FILE
        ):

            return {

                "wins": 0,

                "losses": 0,

                "profit": 0,

                "trades": 0

            }


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


        return {

            "wins": 0,

            "losses": 0,

            "profit": 0,

            "trades": 0

        }




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




def add_result(
    result,
    profit
):

    try:


        data = load_performance()


        data["trades"] += 1



        if result == "WIN":


            data["wins"] += 1



        else:


            data["losses"] += 1



        data["profit"] = round(

            data["profit"] + profit,

            2

        )


        data["last_update"] = (

            datetime.now()

            .strftime(

                "%Y-%m-%d %H:%M:%S"

            )

        )



        save_performance(
            data
        )



        return data



    except Exception as e:


        logger.exception(
            e
        )


        return {}




def get_summary():

    data = load_performance()


    total = data.get(
        "trades",
        0
    )


    win_rate = 0



    if total > 0:


        win_rate = round(

            (

                data["wins"]

                /

                total

            ) * 100,

            2

        )



    return {

        "trades": total,

        "wins": data.get(
            "wins",
            0
        ),

        "losses": data.get(
            "losses",
            0
        ),

        "profit": data.get(
            "profit",
            0
        ),

        "win_rate": win_rate

    }
