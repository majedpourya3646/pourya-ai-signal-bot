# core/market_scheduler.py

import time

from core.logger import logger


DEFAULT_INTERVAL = 300



def run_scheduler(
    task,
    interval=DEFAULT_INTERVAL
):

    logger.info(
        "MARKET SCHEDULER STARTED"
    )


    while True:


        try:


            task()



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            interval
        )
