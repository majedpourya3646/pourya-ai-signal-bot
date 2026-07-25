# core/error_handler.py

from core.logger import logger



def handle_error(
    error,
    context=""
):

    try:

        logger.error(
            f"{context} | ERROR: {error}"
        )


        return {

            "success": False,

            "error": str(error),

            "context": context

        }



    except Exception as e:

        logger.exception(e)

        return {

            "success": False,

            "error": str(e),

            "context": context

        }
