# core/app.py

import time

from core.logger import logger

from core.startup_manager import (
    initialize_system,
    shutdown_system
)

from core.scheduler import (
    start_all_services,
    stop_all_services
)





RUNNING = False





def start():

    global RUNNING


    try:


        logger.info(

            "POURYA TRADER AI STARTING"

        )



        if not initialize_system():


            logger.error(

                "SYSTEM INITIALIZATION FAILED"

            )


            return False





        if not start_all_services():


            logger.error(

                "SERVICES START FAILED"

            )


            return False





        RUNNING = True



        logger.info(

            "POURYA TRADER AI ONLINE"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def run():

    try:


        if not start():

            return False





        while RUNNING:


            time.sleep(

                10

            )



        return True



    except KeyboardInterrupt:


        logger.warning(

            "STOP SIGNAL RECEIVED"

        )


        stop()



        return True



    except Exception as e:


        logger.exception(e)


        stop()



        return False







def stop():

    global RUNNING


    try:


        RUNNING = False



        stop_all_services()



        shutdown_system()



        logger.info(

            "POURYA TRADER AI STOPPED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def status():

    return {


        "running":

            RUNNING

    }
