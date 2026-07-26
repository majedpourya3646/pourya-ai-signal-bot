# core/telegram_bot_manager.py

from core.telegram_commands import (
    process_command
)

from core.telegram_admin import (
    admin_users,
    admin_statistics
)

from core.logger import logger



ADMIN_COMMANDS = [

    "/users",

    "/stats"

]





def handle_message(
    user_id,
    text,
    username=""
):

    try:

        if text in ADMIN_COMMANDS:


            if text == "/users":

                return admin_users()



            if text == "/stats":

                return admin_statistics()




        return process_command(

            user_id,

            text,

            username

        )



    except Exception as e:

        logger.exception(e)

        return "Telegram bot error."





def send_bot_message(
    user_id,
    message
):

    try:

        logger.info(

            f"SEND MESSAGE TO {user_id}: {message}"

        )


        return True



    except Exception as e:

        logger.exception(e)

        return False
