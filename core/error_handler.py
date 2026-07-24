# core/error_handler.py

import traceback

from core.logger import logger

from telegram_sender import send_message



def handle_error(
    error,
    module="SYSTEM",
    notify=False
):

    try:


        error_message = (

            f"❌ Error in {module}\n\n"

            f"{str(error)}"

        )



        logger.error(
            error_message
        )



        logger.error(

            traceback.format_exc()

        )



        if notify:


            send_message(

                error_message

            )



        return {

            "status": False,

            "module": module,

            "error": str(error)

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "status": False,

            "error": str(e)

        }




def safe_execute(
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


        handle_error(
            e,
            function.__name__
        )


        return None
