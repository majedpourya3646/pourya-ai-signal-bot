# core/trading_loop.py

import time

from core.trading_controller import (
    run_trading_cycle
)

from core.position_manager import (
    monitor_positions
)

from core.config_manager import (
    get_setting
)

from core.logger import logger



def run_trading_loop():

    interval = get_setting(
        "scan_interval",
        300
    )


    logger.info(
        "TRADING LOOP STARTED"
    )



    while True:


        try:


            # بررسی معاملات باز

            closed = monitor_positions()



            if closed:


                logger.info(

                    f"CLOSED POSITIONS: {closed}"

                )



            # اجرای چرخه جدید

            result = run_trading_cycle()



            if result:


                logger.info(

                    f"NEW TRADES: {result}"

                )



        except Exception as e:


            logger.exception(
                e
            )



        time.sleep(
            interval
        )



if __name__ == "__main__":


    run_trading_loop()
