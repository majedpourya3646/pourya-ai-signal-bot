# core/telegram_bot_manager.py

import requests

from config import (
    BOT_TOKEN
)

from core.telegram_commands import (
    handle_command
)

from core.logger import logger



TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)



def get_updates(
    offset=None
):

    try:


        params = {}


        if offset:

            params["offset"] = offset



        response = requests.get(

            TELEGRAM_API + "/getUpdates",

            params=params,

            timeout=30

        )



        return response.json()



    except Exception as e:


        logger.exception(
            e
        )


        return {}




def process_updates():

    offset = None



    logger.info(
        "TELEGRAM BOT MANAGER STARTED"
    )



    while True:


        try:


            updates = get_updates(
                offset
            )



            for update in updates.get(
                "result",
                []
            ):


                offset = update["update_id"] + 1



                message = update.get(
                    "message",
                    {}
                )


                text = message.get(
                    "text",
                    ""
                )


                user_id = message.get(
                    "from",
                    {}
                ).get(
                    "id"
                )



                if text.startswith(
                    "/"
                ):


                    handle_command(

                        text,

                        user_id

                    )



        except Exception as e:


            logger.exception(
                e
            )
