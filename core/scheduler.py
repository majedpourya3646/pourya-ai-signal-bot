# core/scheduler.py

import threading
import time

from core.logger import logger

from core.trading_loop import (
    trading_loop,
    stop_loop
)

from core.health_monitor import (
    run_health_check
)

from core.report_manager import (
    generate_report_text
)

from telegram_sender import (
    send_message
)

from config import (
    SCHEDULER_MODE
)





SERVICES = []

RUNNING = False







def health_service():

    while RUNNING:

        try:

            result = run_health_check()

            logger.info(

                f"HEALTH CHECK: {result}"

            )


        except Exception as e:

            logger.exception(e)



        time.sleep(

            300

        )









def report_service():

    while RUNNING:

        try:

            report = generate_report_text()



            if report:

                send_message(

                    report

                )


        except Exception as e:

            logger.exception(e)



        time.sleep(

            86400

        )









def start_service(
    target,
    name
):

    try:


        thread = threading.Thread(

            target=target,

            name=name,

            daemon=True

        )


        thread.start()



        SERVICES.append(

            thread

        )



        logger.info(

            f"SERVICE STARTED {name}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def start_all_services():

    global RUNNING


    try:


        if RUNNING:

            return True



        RUNNING = True





        start_service(

            trading_loop,

            "TradingLoop"

        )



        start_service(

            health_service,

            "HealthMonitor"

        )



        start_service(

            report_service,

            "ReportService"

        )





        logger.info(

            f"ALL SERVICES STARTED MODE={SCHEDULER_MODE}"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def stop_all_services():

    global RUNNING


    try:


        RUNNING = False



        stop_loop()



        logger.info(

            "ALL SERVICES STOPPED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def scheduler_status():

    return {


        "running":

            RUNNING,


        "services":

            [

                x.name

                for x in SERVICES

            ]

    }
