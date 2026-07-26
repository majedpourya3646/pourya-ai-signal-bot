# core/startup_manager.py

from core.database_manager import (
    init_database
)

from core.health_monitor import (
    check_database
)

from core.logger import logger



def initialize_system():

    try:

        logger.info(
            "INITIALIZING SYSTEM"
        )



        if not init_database():

            logger.error(
                "DATABASE INITIALIZATION FAILED"
            )

            return False



        if not check_database():

            logger.error(
                "DATABASE CHECK FAILED"
            )

            return False



        logger.info(
            "SYSTEM READY"
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False




def shutdown_system():

    try:

        logger.info(
            "SYSTEM SHUTDOWN"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
