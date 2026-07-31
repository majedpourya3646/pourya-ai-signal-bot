# core/startup_manager.py

from core.logger import logger

from core.database_manager import (
    initialize_database
)

from core.health_monitor import (
    run_health_check
)

from telegram_sender import (
    send_message
)

from config import (
    BOT_NAME,
    PAPER_TRADING,
    MARKET_TYPE
)





SYSTEM_READY = False









def check_configuration():

    try:


        required = [

            BOT_NAME,

            MARKET_TYPE

        ]



        for item in required:


            if not item:

                return False



        return True



    except Exception as e:


        logger.exception(e)


        return False







def initialize_system():

    global SYSTEM_READY


    try:


        logger.info(

            "SYSTEM INITIALIZATION STARTED"

        )





        if not check_configuration():


            logger.error(

                "CONFIGURATION ERROR"

            )


            return False





        if not initialize_database():


            logger.error(

                "DATABASE INITIALIZATION FAILED"

            )


            return False







        health = run_health_check()



        if not health.get(

            "online"

        ):


            logger.warning(

                f"PARTIAL HEALTH STATUS {health}"

            )







        send_start_message()



        SYSTEM_READY = True



        logger.info(

            "SYSTEM READY"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def send_start_message():

    try:


        mode = (

            "PAPER"

            if PAPER_TRADING

            else

            "LIVE"

        )



        message = f"""

<b>🤖 {BOT_NAME}</b>


✅ System Started


⚙️ Market:
{MARKET_TYPE}


📝 Mode:
{mode}


🟢 Engine Ready

"""



        send_message(

            message

        )



    except Exception as e:


        logger.exception(e)









def shutdown_system():

    global SYSTEM_READY


    try:


        SYSTEM_READY = False



        logger.info(

            "SYSTEM SHUTDOWN COMPLETE"

        )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def system_status():

    return {


        "ready":

            SYSTEM_READY

    }
