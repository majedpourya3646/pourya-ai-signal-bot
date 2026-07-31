# bot.py

import signal

import sys

from core.logger import logger

from core.app import (
    start,
    stop
)

from telegram_sender import (
    send_message
)





RUNNING = False







def shutdown_handler(
    signum,
    frame
):

    try:


        logger.warning(

            "SHUTDOWN SIGNAL RECEIVED"

        )



        stop()



        sys.exit(0)



    except Exception as e:


        logger.exception(e)


        sys.exit(1)









def startup_message():

    try:


        send_message(

            """

🤖 <b>Pourya Trader AI v2.0.0</b>


✅ SYSTEM ONLINE


🟢 Trading Engine Started

🟢 CoinEx Connector Ready

🟡 Paper Trading Mode Enabled


Waiting for opportunities...

"""

        )



    except Exception as e:


        logger.exception(e)









def main():

    global RUNNING


    try:


        signal.signal(

            signal.SIGINT,

            shutdown_handler

        )


        signal.signal(

            signal.SIGTERM,

            shutdown_handler

        )





        logger.info(

            "BOT STARTING"

        )





        if not start():


            logger.error(

                "BOT START FAILED"

            )


            return False





        startup_message()



        RUNNING = True





        while RUNNING:


            signal.pause()



        return True



    except Exception as e:


        logger.exception(e)


        stop()


        return False







if __name__ == "__main__":

    main()
