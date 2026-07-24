# core/final_engine.py

from core.startup_manager import (
    initialize_system
)

from core.market_monitor import (
    run_market_monitor
)

from core.report_scheduler import (
    run_report_scheduler
)

from core.monthly_scheduler import (
    run_monthly_scheduler
)

from core.telegram_bot_manager import (
    process_updates
)

from core.logger import logger

import threading



def start_final_engine():

    try:


        logger.info(
            "FINAL ENGINE STARTING"
        )



        if not initialize_system():


            return False



        threads = []



        tasks = [

            run_market_monitor,

            run_report_scheduler,

            run_monthly_scheduler,

            process_updates

        ]



        for task in tasks:


            thread = threading.Thread(

                target=task

            )


            thread.daemon = True


            thread.start()


            threads.append(
                thread
            )



        logger.info(
            "ALL ENGINE MODULES STARTED"
        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




if __name__ == "__main__":


    start_final_engine()
