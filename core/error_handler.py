# core/error_handler.py

from core.logger import logger



def handle_error(
    error,
    context=""
):

    try:

        message = str(
            error
        )


        if context:

            logger.error(
                f"{context}: {message}"
            )

        else:

            logger.error(
                message
            )


        return {

            "success": False,

            "error": message,

            "context": context

        }



    except Exception as e:

        logger.exception(e)

        return {

            "success": False,

            "error": str(e)

        }





def safe_error(
    func,
    *args,
    **kwargs
):

    try:

        return func(
            *args,
            **kwargs
        )


    except Exception as e:

        handle_error(
            e,
            func.__name__
        )

        return None
