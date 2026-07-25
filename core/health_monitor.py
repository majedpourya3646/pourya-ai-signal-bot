# core/health_monitor.py

from core.database_manager import (
    execute_query
)

from core.logger import logger



def check_database():

    try:

        result = execute_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """
        )


        if result:

            return True


        return False



    except Exception as e:

        logger.exception(e)

        return False





def get_system_health():

    try:

        database_status = check_database()


        return {

            "database": (
                "OK"
                if database_status
                else "FAILED"
            ),

            "status": (
                "HEALTHY"
                if database_status
                else "ERROR"
            )

        }



    except Exception as e:

        logger.exception(e)

        return {

            "database": "ERROR",

            "status": "ERROR"

        }
