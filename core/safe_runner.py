# core/safe_runner.py

import traceback

from core.system_health import (
    is_system_ready
)

from core.logger import logger



def safe_execute(
    func,
    *args,
    **kwargs
):

    try:

        if not is_system_ready():

            logger.error(
                "SYSTEM NOT READY"
            )

            return None



        return func(
            *args,
            **kwargs
        )



    except Exception as e:

        logger.error(
            str(e)
        )

        logger.error(
            traceback.format_exc()
        )

        return None





def safe_loop(
    func,
    interval
):

    import time



    while True:

        safe_execute(
            func
        )

        time.sleep(
            interval
        )
