# core/scheduler.py

import threading

import time

from core.logger import logger

from config import (
    SCHEDULER_INTERVAL
)

from core.auto_trader import (
    execute_trade
)

from core.position_manager import (
    check_tp_sl
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





RUNNING = False

THREADS = []








def trading_loop():

    global RUNNING


    logger.info(

        "TRADING LOOP STARTED"

    )



    while RUNNING:


        try:


            execute_trade()



        except Exception as e:


            logger.exception(e)



        time.sleep(

            SCHEDULER_INTERVAL

        )









def position_loop():

    global RUNNING


    logger.info(

        "POSITION MONITOR STARTED"

    )



    while RUNNING:


        try:


            closed = check_tp_sl()



            for trade in closed:


                logger.info(

                    f"CLOSED {trade}"

                )



        except Exception as e:


            logger.exception(e)



        time.sleep(

            15

        )









def health_loop():

    global RUNNING


    logger.info(

        "HEALTH MONITOR STARTED"

    )



    while RUNNING:


        try:


            run_health_check()



        except Exception as e:


            logger.exception(e)



        time.sleep(

            300

        )









def report_loop():

    global RUNNING


    logger.info(

        "REPORT SERVICE STARTED"

    )



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









def start_all_services():

    global RUNNING


    try:


        RUNNING = True



        services = [

            trading_loop,

            position_loop,

            health_loop,

            report_loop

        ]



        for service in services:


            thread = threading.Thread(

                target=service,

                daemon=True

            )



            THREADS.append(

                thread

            )



            thread.start()





        logger.info(

            "ALL SERVICES STARTED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def stop_all_services():

    global RUNNING


    try:


        RUNNING = False



        logger.info(

            "ALL SERVICES STOPPED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False
