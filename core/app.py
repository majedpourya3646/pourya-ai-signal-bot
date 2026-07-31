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






APP_RUNNING = False








def start_app():

    global APP_RUNNING


    try:


        logger.info(

            "APPLICATION STARTING"

        )





        if not initialize_system():


            logger.error(

                "SYSTEM INITIALIZATION FAILED"

            )


            return False






        if not start_all_services():


            logger.error(

                "SERVICE START FAILED"

            )


            return False





        APP_RUNNING = True



        logger.info(

            "POURYA TRADER AI RUNNING"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False









def run_forever():

    global APP_RUNNING


    try:


        if not APP_RUNNING:


            if not start_app():

                return





        while APP_RUNNING:


            time.sleep(

                10

            )



    except KeyboardInterrupt:


        stop_app()



    except Exception as e:


        logger.exception(e)


        stop_app()







def stop_app():

    global APP_RUNNING


    try:


        logger.info(

            "APPLICATION STOPPING"

        )



        stop_all_services()



        shutdown_system()



        APP_RUNNING = False



        logger.info(

            "APPLICATION STOPPED"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False
