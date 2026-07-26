# core/app.py

from core.scheduler import (
    start_all_services
)

from core.startup_manager import (
    initialize_system,
    shutdown_system
)

from core.version import (
    version_string
)

from core.logger import logger





def start():

    try:

        logger.info(
            version_string()
        )



        if not initialize_system():

            logger.error(
                "STARTUP FAILED"
            )

            return False



        start_all_services()



        return True



    except Exception as e:

        logger.exception(e)

        return False





def stop():

    try:

        shutdown_system()



        logger.info(
            "APPLICATION STOPPED"
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False





if __name__ == "__main__":

    start()
