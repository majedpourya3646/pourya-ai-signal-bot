# core/system_initializer.py

from core.database_manager import (
    init_database
)

from core.performance_tracker import (
    create_performance_table
)

from core.profit_share import (
    create_profit_share_table
)

from core.logger import logger



def initialize():

    try:

        logger.info(
            "INITIALIZING DATABASE"
        )



        steps = [

            init_database,

            create_performance_table,

            create_profit_share_table

        ]



        for step in steps:

            if not step():

                logger.error(
                    f"INITIALIZATION FAILED: {step.__name__}"
                )

                return False



        logger.info(
            "ALL TABLES CREATED"
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False




def startup():

    try:

        if not initialize():

            logger.error(
                "INITIALIZATION FAILED"
            )

            return False



        logger.info(
            "SYSTEM STARTED SUCCESSFULLY"
        )



        return True



    except Exception as e:

        logger.exception(e)

        return False
