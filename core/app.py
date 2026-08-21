# core/app.py

import time


from core.logger import logger


from core.database import (
    initialize_database
)


from core.mt5_connector import (
    initialize_mt5,
    shutdown_mt5
)


from core.telegram import (
    send_message
)


from core.position_monitor import (
    start_position_monitor
)


from scheduler.trading_loop import (
    start_trading_loop
)


from core.health_monitor import (
    start_health_monitor
)


from core.report_service import (
    start_report_service
)





def initialize_system():

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

        "MT5 CONNECTION READY"

    )



    return True





def start_services():


    logger.info(
        "STARTING SERVICES"
    )



    start_trading_loop()



    start_position_monitor()



    start_health_monitor()



    start_report_service()



    logger.info(
        "ALL SERVICES STARTED"
    )







def run():


    logger.info(
        "APPLICATION STARTING"
    )



    if not initialize_system():
        return

        logger.error(
            "SYSTEM START FAILED"
        )


        return




    send_message(

        """

🤖 Pourya Trader AI

✅ MT5 Connected

✅ Trading Engine Started

✅ Position Monitor Active


"""

    )



    start_services()



    logger.info(
        "POURYA TRADER AI RUNNING"
    )



    try:


        while True:


            time.sleep(
                60
            )



    except KeyboardInterrupt:


        logger.info(
            "SYSTEM STOPPING"
        )


        shutdown_mt5()



        logger.info(
            "SYSTEM STOPPED"
        )
