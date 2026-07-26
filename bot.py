# bot.py

from core.app import (
    start,
    stop
)

from core.logger import logger





def main():

    try:

        logger.info(
            "STARTING POURYA TRADER AI BOT"
        )


        start()



    except KeyboardInterrupt:


        logger.info(
            "BOT STOPPED BY USER"
        )


        stop()



    except Exception as e:

        logger.exception(e)


        stop()





if __name__ == "__main__":

    main()
