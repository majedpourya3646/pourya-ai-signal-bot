# core/startup_manager.py

from core.database_manager import (
    init_database
)

from core.logger import logger



def initialize_system():

    try:

        logger.info(
            "SYSTEM INITIALIZATION STARTED"
        )


        database_ready = init_database()


        if not database_ready:

            logger.error(
                "DATABASE INITIALIZATION FAILED"
            )

            return False



        logger.info(
            "DATABASE READY"
        )


        logger.info(
            "SYSTEM INITIALIZATION COMPLETED"
        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
