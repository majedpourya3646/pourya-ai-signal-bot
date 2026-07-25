# core/market_cache.py

import time

from core.logger import logger



CACHE = {}


DEFAULT_CACHE_TIME = 60





def set_cache(
    key,
    value,
    expire=DEFAULT_CACHE_TIME
):

    try:

        CACHE[key] = {

            "value": value,

            "time": time.time(),

            "expire": expire

        }


        return True



    except Exception as e:

        logger.exception(e)

        return False





def get_cache(
    key
):

    try:

        item = CACHE.get(
            key
        )


        if not item:

            return None



        if (
            time.time()
            -
            item["time"]
        ) > item["expire"]:


            delete_cache(
                key
            )


            return None



        return item["value"]



    except Exception as e:

        logger.exception(e)

        return None





def delete_cache(
    key
):

    try:

        if key in CACHE:

            del CACHE[key]


        return True



    except Exception as e:

        logger.exception(e)

        return False





def clear_cache():

    try:

        CACHE.clear()

        return True



    except Exception as e:

        logger.exception(e)

        return False
