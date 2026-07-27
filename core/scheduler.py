# core/scheduler.py

import time
import threading
import os

from core.trading_loop import (
    run_loop
)

from core.report_scheduler import (
    start_report_scheduler
)

from core.logger import logger


MODE = os.getenv(
    "BOT_MODE",
    "TEST"
)


def start_trading_thread():

    try:

        thread = threading.Thread(

            target=run_loop,

            daemon=False

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

        logger.info(
            f"SCHEDULER MODE: {MODE}"
        )

        trading_thread = start_trading_thread()

        if MODE == "LIVE":

            start_report_thread()

            while True:

                time.sleep(60)

        if MODE == "TEST":

            logger.info(
                "TEST MODE ENABLED"
            )

    run_loop()

    return True

            if trading_thread:

                trading_thread.join()

            return True

    except KeyboardInterrupt:

        logger.info(
            "SCHEDULER STOPPED"
        )

        return True

    except Exception as e:

        logger.exception(e)

        return False
