# core/system_health.py

from core.health_monitor import (
    get_system_health
)

from core.logger import logger



def system_status():

    try:

        health = get_system_health()


        logger.info(
            f"SYSTEM STATUS: {health}"
        )


        return health



    except Exception as e:

        logger.exception(e)


        return {

            "status": "ERROR",

            "database": "UNKNOWN"

        }
