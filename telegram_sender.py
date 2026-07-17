from config import (
    BOT_TOKEN,
    CHAT_ID
)

from core.session import session
from core.logger import logger



TELEGRAM_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
)



def send_message(
    text,
    parse_mode="HTML",
    disable_preview=True
):


    if not BOT_TOKEN or not CHAT_ID:

        logger.error(
            "BOT_TOKEN or CHAT_ID missing"
        )

        return False



    if len(text) > 4000:

        text = text[:4000]



    payload = {

        "chat_id": CHAT_ID,

        "text": text,

        "parse_mode": parse_mode,

        "disable_web_page_preview": disable_preview

    }



    try:

        response = session.post(

            TELEGRAM_URL,

            data=payload

        )



        logger.info(

            f"Telegram status: {response.status_code}"

        )



        if response.status_code != 200:

            logger.error(
                response.text
            )

            return False



        result = response.json()



        if not result.get("ok"):

            logger.error(
                result
            )

            return False



        return True



    except Exception as e:

        logger.exception(
            e
        )

        return False
