# core/main_engine.py

from core.engine_connector import (
    run_full_engine
)

from core.config_validator import (
    validate_config
)

from core.startup_manager import (
    initialize_system
)

from core.logger import logger



ENGINE_RUNNING = False





def run_main_engine():

    global ENGINE_RUNNING



    try:

        if ENGINE_RUNNING:

            return False



        if not validate_config():

            logger.error(
                "CONFIG VALIDATION FAILED"
            )

            return False



        if not initialize_system():

            logger.error(
                "SYSTEM INIT FAILED"
            )

            return False



        ENGINE_RUNNING = True



        logger.info(
            "MAIN ENGINE STARTED"
        )



        result = run_full_engine()



        logger.info(
            f"ENGINE RESULT: {result}"
        )



        return result



    except Exception as e:

        logger.exception(e)

        return None





def stop_engine():

    global ENGINE_RUNNING



    try:

        ENGINE_RUNNING = False



        logger.info(
            "MAIN ENGINE STOPPED"
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False





def engine_status():

    return {

        "running": ENGINE_RUNNING

    }
