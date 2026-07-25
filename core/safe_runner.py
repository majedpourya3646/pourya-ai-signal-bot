# core/safe_runner.py

from core.logger import logger


def run_safe(
    function,
    *args,
    **kwargs
):

    try:

        return function(
            *args,
            **kwargs
        )


    except Exception as e:

        logger.exception(e)

        return None
