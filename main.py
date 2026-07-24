# main.py

import time

from core.main_engine import (
    run_main_engine
)

from core.trading_loop import (
    run_trading_loop
)

from core.telegram_bot_manager import (
    process_updates
)

from core.report_scheduler import (
    run_report_scheduler
)

from core.monthly_scheduler import (
    run_monthly_scheduler
)

from core.health_monitor import (
    run_health_monitor
)

from core.logger import logger

import threading



def start_services():

    services = [

        run_main_engine,

        run_trading_loop,

        process_updates,

        run_report_scheduler,

        run_monthly_scheduler,

        run_health_monitor

    ]



    for service in services:


        thread = threading.Thread(

            target=service

        )


        thread.daemon = True


        thread.start()



        logger.info(

            f"SERVICE STARTED: {service.__name__}"

        )




def main():

    try:


        logger.info(

            "🚀 POURYA TRADER AI STARTING"

        )



        start_services()



        while True:


            time.sleep(
                60
            )



    except KeyboardInterrupt:


        logger.info(

            "SYSTEM STOPPED BY USER"

        )



    except Exception as e:


        logger.exception(
            e
        )




if __name__ == "__main__":


    main()
