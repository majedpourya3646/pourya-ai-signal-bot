# core/scheduler.py

import threading

import time

from datetime import datetime

from core.logger import logger

from core.trading_loop import (
    run_loop
)

from core.config_manager import (
    get_setting
)




SERVICES = []





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

            {

                "name":

                    name,


                "thread":

                    thread,


                "started":

                    datetime.utcnow().isoformat()

            }

        )


        logger.info(
            f"SERVICE STARTED: {name}"
        )


        return True



    except Exception as e:


        logger.exception(e)


        return False






def health_monitor():

    try:


        while True:



            for service in SERVICES:


                thread = service.get(
                    "thread"
                )


                if thread and not thread.is_alive():


                    logger.error(

                        f"SERVICE STOPPED: {service.get('name')}"

                    )



            interval = get_setting(

                "health_check_interval",

                60

            )



            time.sleep(
                int(interval)
            )



    except Exception as e:


        logger.exception(e)







def daily_report_service():

    try:


        while True:


            now = datetime.now()



            if now.hour == 0 and now.minute == 0:


                logger.info(

                    "DAILY REPORT TRIGGER"

                )


                # اتصال به Report Generator

                # در مرحله بعد کامل می‌شود



                time.sleep(
                    60
                )



            time.sleep(
                30
            )



    except Exception as e:


        logger.exception(e)







def start_all_services():

    try:



        SERVICES.clear()



        trading = start_service(

            run_loop,

            "TRADING_ENGINE"

        )



        reports = start_service(

            daily_report_service,

            "REPORT_SERVICE"

        )



        monitor = start_service(

            health_monitor,

            "HEALTH_MONITOR"

        )



        return all([

            trading,

            reports,

            monitor

        ])



    except Exception as e:


        logger.exception(e)


        return False





def stop_all_services():

    try:


        SERVICES.clear()


        logger.info(

            "ALL SERVICES STOP REQUESTED"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False
