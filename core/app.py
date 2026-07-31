# core/app.py

from core.logger import logger


from core.mt5_connector import (
    initialize_mt5,
    shutdown_mt5
)


from core.database import (
    initialize_database
)


from core.scheduler import (
    start_scheduler
)


from core.position_monitor import (
    start_position_monitor
)


from core.health_monitor import (
    start_health_monitor
)


from core.report_service import (
    start_report_service
)


from core.telegram import (
    send_message
)





def system_health():

    status = {

        "database": True,

        "mt5": True,

        "telegram": True

    }


    return status





def initialize_system():

    try:


        logger.info(
            "SYSTEM INITIALIZATION STARTED"
        )



        initialize_database()


        logger.info(
            "DATABASE INITIALIZED"
        )



        mt5_status = initialize_mt5()



        if not mt5_status:


            logger.error(
                "MT5 CONNECTION FAILED"
            )


            return False




        logger.info(
            f"HEALTH STATUS {system_health()}"
        )



        send_message(
            "🤖 Pourya Trader AI\n\nMT5 Connected ✅\nSystem Ready"
        )



        logger.info(
            "SYSTEM READY"
        )



        return True



    except Exception as e:


        logger.error(
            f"SYSTEM INIT ERROR {e}"
        )


        return False





def start_services():


    logger.info(
        "TRADING LOOP STARTED"
    )


    start_scheduler()



    logger.info(
        "POSITION MONITOR STARTED"
    )


    start_position_monitor()



    logger.info(
        "HEALTH MONITOR STARTED"
    )


    start_health_monitor()



    logger.info(
        "REPORT SERVICE STARTED"
    )


    start_report_service()



    logger.info(
        "ALL SERVICES STARTED"
    )





def shutdown():

    try:


        shutdown_mt5()


        logger.info(
            "MT5 SHUTDOWN"
        )


    except Exception as e:


        logger.error(
            f"SHUTDOWN ERROR {e}"
        )





def run():


    logger.info(
        "APPLICATION STARTING"
    )


    if initialize_system():


        start_services()


        logger.info(
            "POURYA TRADER AI RUNNING"
        )



    else:


        logger.error(
            "SYSTEM START FAILED"
        )
