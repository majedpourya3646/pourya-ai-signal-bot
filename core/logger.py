# core/logger.py

import logging
import os

from datetime import datetime



LOG_FOLDER = "logs"



def setup_logger():

    os.makedirs(

        LOG_FOLDER,

        exist_ok=True

    )


    logger = logging.getLogger(
        "PouryaTraderAI"
    )


    logger.setLevel(
        logging.INFO
    )



    if not logger.handlers:


        file_handler = logging.FileHandler(

            os.path.join(

                LOG_FOLDER,

                f"bot_{datetime.now().strftime('%Y%m%d')}.log"

            ),

            encoding="utf-8"

        )



        console_handler = logging.StreamHandler()



        formatter = logging.Formatter(

            "%(asctime)s | %(levelname)s | %(message)s"

        )



        file_handler.setFormatter(
            formatter
        )


        console_handler.setFormatter(
            formatter
        )



        logger.addHandler(
            file_handler
        )


        logger.addHandler(
            console_handler
        )



    return logger




logger = setup_logger()
