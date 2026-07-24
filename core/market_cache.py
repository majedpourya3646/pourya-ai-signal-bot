# core/market_cache.py

import json
import os
import time

from core.logger import logger


CACHE_FILE = "data/market_cache.json"

CACHE_TIME = 300



def save_cache(data):

    try:

        os.makedirs(
            "data",
            exist_ok=True
        )


        payload = {

            "timestamp": time.time(),

            "data": data

        }


        with open(
            CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(

                payload,

                file,

                ensure_ascii=False,

                indent=4

            )


    except Exception as e:


        logger.exception(
            e
        )




def load_cache():

    try:


        if not os.path.exists(
            CACHE_FILE
        ):

            return None



        with open(

            CACHE_FILE,

            "r",

            encoding="utf-8"

        ) as file:


            payload = json.load(
                file
            )



        timestamp = payload.get(
            "timestamp",
            0
        )



        if (

            time.time() - timestamp

        ) > CACHE_TIME:


            return None



        return payload.get(
            "data",
            []
        )



    except Exception as e:


        logger.exception(
            e
        )


        return None
