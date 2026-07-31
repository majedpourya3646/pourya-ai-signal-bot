# core/trading_loop.py

import time

from threading import Event

from core.logger import logger

from core.trading_controller import (
    run_trading_cycle
)

from config import (
    TRADING_INTERVAL
)





STOP_EVENT = Event()

RUNNING = False







def trading_loop():

    global RUNNING

    try:

        RUNNING = True


        logger.info(

            "TRADING LOOP STARTED"

        )



        while not STOP_EVENT.is_set():



            try:


                result = run_trading_cycle()



                if result:

                    logger.info(

                        f"TRADING RESULT: {result}"

                    )



            except Exception as e:


                logger.exception(e)





            STOP_EVENT.wait(

                TRADING_INTERVAL

            )



    except Exception as e:


        logger.exception(e)



    finally:


        RUNNING = False



        logger.info(

            "TRADING LOOP STOPPED"

        )









def start_loop():

    try:


        if RUNNING:

            return False



        STOP_EVENT.clear()



        trading_loop()



        return True



    except Exception as e:


        logger.exception(e)


        return False







def stop_loop():

    try:


        STOP_EVENT.set()



        logger.info(

            "STOP SIGNAL SENT"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def loop_status():

    return {


        "running":

            RUNNING,


        "interval":

            TRADING_INTERVAL

    }
