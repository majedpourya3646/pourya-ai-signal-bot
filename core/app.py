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

from telegram_sender import (
    send_message
)



def start():

    try:

        logger.info(
            "STARTING POURYA TRADER AI BOT"
        )


        logger.info(
            version_string()
        )



        if not initialize_system():

            logger.error(
                "STARTUP FAILED"
            )

            return False



        logger.info(
            "SYSTEM READY"
        )



        send_message(
            """
🤖 <b>Pourya Trader AI v2.0.0</b>

✅ SYSTEM ONLINE

🟢 CoinEx API: Connected
🟢 AI Engine: Running
🟡 Paper Trading: Enabled

Waiting for opportunities...
"""
        )



        result = start_all_services()



        return bool(result)



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
