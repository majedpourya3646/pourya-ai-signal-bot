import logging
import os


os.makedirs(
    "logs",
    exist_ok=True
)


LOG_FILE = "logs/bot.log"



logger = logging.getLogger(
    "PouryaTraderAI"
)


logger.setLevel(
    logging.INFO
)



formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)



if not logger.handlers:


    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )


    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )


    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )
