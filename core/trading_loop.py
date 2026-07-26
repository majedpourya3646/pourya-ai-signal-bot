# core/trading_loop.py

import time

from core.trading_controller import (
    run_trading_cycle
)

from core.position_manager import (
    check_tp_sl
)

from core.logger import logger

from core.config_manager import (
    get_setting
)



def run_loop():

    try:

        logger.info(
            "TRADING LOOP STARTED"
        )



        while True:


            try:


                closed = check_tp_sl()


                if closed:

                    logger.info(
                        f"CLOSED POSITIONS: {closed}"
                    )



                trades = run_trading_cycle()



                if trades:

                    logger.info(
                        f"EXECUTED TRADES: {trades}"
                    )



                interval = get_setting(

                    "trading_interval",

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

    run_loop()
