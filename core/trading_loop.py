# core/trading_loop.py

import time

from core.final_engine import (
    run_final_engine
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def run_loop():

    logger.info(
        "TRADING LOOP STARTED"
    )


    while True:

        try:

            result = run_final_engine()


            logger.info(
                f"LOOP RESULT: {result}"
            )


            interval = get_setting(
                "loop_interval",
                60
            )


            time.sleep(
                interval
            )



        except KeyboardInterrupt:

            logger.info(
                "TRADING LOOP STOPPED BY USER"
            )

            break



        except Exception as e:

            logger.exception(e)

            time.sleep(
                30
            )



if __name__ == "__main__":

    run_loop()
