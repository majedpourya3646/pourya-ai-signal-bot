# core/market_scheduler.py

import time

from core.final_engine import (
    run_final_engine
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def start_scheduler():

    try:

        logger.info(
            "MARKET SCHEDULER STARTED"
        )


        while True:


            try:

                result = run_final_engine()


                logger.info(
                    f"SCHEDULER RESULT: {result}"
                )



                interval = get_setting(

                    "scheduler_interval",

                    300

                )


                time.sleep(
                    interval
                )



            except Exception as e:

                logger.exception(e)

                time.sleep(
                    60
                )



    except Exception as e:

        logger.exception(e)



if __name__ == "__main__":

    start_scheduler()
