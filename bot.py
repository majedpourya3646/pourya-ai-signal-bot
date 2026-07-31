# bot.py

import sys

from core.logger import logger

from core.app import (
    run_forever,
    stop_app
)







def main():

    try:


        logger.info(

            "STARTING POURYA TRADER AI"

        )



        run_forever()



    except KeyboardInterrupt:


        logger.info(

            "STOP SIGNAL RECEIVED"

        )


        stop_app()



    except Exception as e:


        logger.exception(e)


        stop_app()



        sys.exit(1)








if __name__ == "__main__":


    main()
