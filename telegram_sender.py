# telegram_sender.py

import requests

from config import (
    BOT_TOKEN,
    CHAT_ID
)

from core.logger import logger



TELEGRAM_URL = (
    "https://api.telegram.org/bot"
    + BOT_TOKEN
    + "/sendMessage"
)



def send_message(
    message
):

    try:


        if not BOT_TOKEN or not CHAT_ID:

            logger.error(
                "Telegram config missing"
            )

            return False



        payload = {

            "chat_id": CHAT_ID,

            "text": message,

            "parse_mode": "HTML"

        }



        response = requests.post(

            TELEGRAM_URL,

            json=payload,

            timeout=20

        )



        logger.info(

            f"Telegram status: {response.status_code}"

        )



        return response.status_code == 200



    except Exception as e:


        logger.exception(
            e
        )


        return False
