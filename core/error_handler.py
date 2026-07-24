# core/error_handler.py

import traceback

from telegram_sender import send_message

from core.logger import logger



def handle_error(
    error,
    location=""
):

    try:


        error_text = str(
            error
        )



        logger.error(

            f"ERROR {location}: {error_text}"

        )



        details = traceback.format_exc()



        message = f"""

🚨 <b>خطای سیستم Pourya Trader AI</b>


📍 بخش:
{location}


❌ خطا:
{error_text}


⚙️ سیستم همچنان فعال است


🤖 Pourya Trader AI

"""



        send_message(
            message
        )



        return details



    except Exception as e:


        logger.exception(
            e
        )


        return None




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
