# core/system_health.py

from core.health_monitor import (
    system_health
)

from core.trade_manager import (
    total_open_trades
)

from core.performance_tracker import (
    get_statistics
)

from core.logger import logger



def get_system_status():

    try:

        health = system_health()

        stats = get_statistics()



        status = {

            "healthy": (

                health.get(
                    "database",
                    False
                )

                and

                health.get(
                    "disk",
                    {}
                ).get(
                    "healthy",
                    False
                )

            ),

            "database": health.get(
                "database",
                False
            ),

            "disk": health.get(
                "disk",
                {}
            ),

            "open_trades": total_open_trades(),

            "statistics": stats,

            "timestamp": health.get(
                "timestamp",
                0
            )

        }



        return status



    except Exception as e:

        logger.exception(e)

        return {

            "healthy": False

        }





def is_system_ready():

    try:

        return get_system_status().get(
            "healthy",
            False
        )

    except Exception as e:

        logger.exception(e)

        return False
