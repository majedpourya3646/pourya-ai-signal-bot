# main.py

import sys

from core.logger import logger

from bot import (
    main as start_bot
)





def run():

    try:

        logger.info(
            "STARTING POURYA TRADER AI"
        )

        start_bot()

    except KeyboardInterrupt:

        logger.warning(
            "APPLICATION STOPPED BY USER"
        )

    except Exception as e:

        logger.exception(e)

        sys.exit(1)





if __name__ == "__main__":

    run()
