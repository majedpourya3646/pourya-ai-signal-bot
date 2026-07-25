# core/logger.py

import logging
import os
from datetime import datetime



LOG_FOLDER = "logs"



os.makedirs(
    LOG_FOLDER,
    exist_ok=True
)



LOG_FILE = (

    f"{LOG_FOLDER}/"

    +

    datetime.now()
    .strftime(
        "%Y-%m-%d"
    )

    +

    ".log"

)



logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),

    handlers=[

        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),

        logging.StreamHandler()

    ]

)



logger = logging.getLogger(
    "PouryaTraderAI"
)
