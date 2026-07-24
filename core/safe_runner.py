# core/safe_runner.py

import time

from core.error_handler import (
    handle_error
)

from core.logger import logger



def run_safe(
    task,
    interval=300,
    name=""
):

    logger.info(
        f"SAFE RUNNER STARTED: {name}"
    )



    while True:


        try:


            task()



        except Exception as e:


            handle_error(

                e,

                name

            )



        time.sleep(
            interval
        )
