# core/launcher.py

from core.main_engine import (
    run_main_engine
)

from core.market_scheduler import (
    start_scheduler
)

from core.startup_manager import (
    initialize_system
)

from core.logger import logger



def start_application():

    try:

        logger.info(
            "STARTING POURYA TRADER AI"
        )



        if not initialize_system():

            logger.error(
                "SYSTEM INITIALIZATION FAILED"
            )

            return False



        run_main_engine()



        return True



    except Exception as e:

        logger.exception(e)

        return False





def start_background():

    try:

        start_scheduler()



    except Exception as e:

        logger.exception(e)
