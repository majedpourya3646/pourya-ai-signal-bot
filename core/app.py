# core/app.py

import time

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

from core.config_manager import (
    get_setting
)

from telegram_sender import (
    send_message
)



APPLICATION_STATUS = {

    "running": False,

    "started_at": None

}



def send_startup_report():

    try:


        paper = get_setting(
            "paper_trading",
            True
        )


        mode = (
            "PAPER"
            if paper
            else
            "REAL"
        )


        message = f"""

🤖 <b>Pourya Trader AI</b>

Version:
{version_string()}


✅ SYSTEM ONLINE


🟢 Trading Engine: Ready

🟢 Risk Engine: Ready

🟢 Database: Connected

🟢 Scheduler: Running


Mode:
{mode}


Waiting for opportunities...

"""


        send_message(
            message
        )


    except Exception as e:

        logger.exception(e)



def start():

    try:


        logger.info(
            "STARTING POURYA TRADER AI"
        )



        logger.info(
            version_string()
        )



        emergency = get_setting(
            "emergency_mode",
            False
        )


        if emergency:


            logger.error(
                "SYSTEM BLOCKED - EMERGENCY MODE"
            )


            return False



        if not initialize_system():


            logger.error(
                "STARTUP FAILED"
            )


            return False



        APPLICATION_STATUS["running"] = True



        logger.info(
            "SYSTEM READY"
        )



        send_startup_report()



        result = start_all_services()



        if not result:


            logger.error(
                "SERVICE START FAILED"
            )


            stop()

            return False



        return True



    except Exception as e:


        logger.exception(e)


        return False




def stop():

    try:


        logger.info(
            "STOPPING APPLICATION"
        )


        APPLICATION_STATUS["running"] = False



        shutdown_system()



        send_message(
            """
🤖 <b>Pourya Trader AI</b>

🔴 SYSTEM OFFLINE

All services stopped safely.
"""
        )



        logger.info(
            "APPLICATION STOPPED"
        )


        return True



    except Exception as e:


        logger.exception(e)


        return False





def get_status():

    return APPLICATION_STATUS




if __name__ == "__main__":

    start()
