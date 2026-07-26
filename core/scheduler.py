# core/scheduler.py

import time
import threading

from core.trading_loop import (
    run_loop
)

from core.report_scheduler import (
    start_report_scheduler
)

from core.logger import logger





def start_trading_thread():

    try:

        thread = threading.Thread(

            target=run_loop,

            daemon=True

        )


        thread.start()



        logger.info(
            "TRADING THREAD STARTED"
        )


        return thread



    except Exception as e:

        logger.exception(e)

        return None





def start_report_thread():

    try:

        thread = threading.Thread(

            target=start_report_scheduler,

            daemon=True

        )


        thread.start()



        logger.info(
            "REPORT THREAD STARTED"
        )


        return thread



    except Exception as e:

        logger.exception(e)

        return None





def start_all_services():

    try:

        start_trading_thread()


        start_report_thread()



        logger.info(
            "ALL SERVICES STARTED"
        )


        while True:

            time.sleep(
                60
            )



    except KeyboardInterrupt:


        logger.info(
            "SERVICES STOPPED"
        )



    except Exception as e:

        logger.exception(e)
