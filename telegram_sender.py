from config import (
    BOT_TOKEN,
    CHAT_ID
)

from core.session import session
from core.logger import logger


def send_message(
    text,
    parse_mode="HTML",
    disable_preview=True
):

    if not BOT_TOKEN or not CHAT_ID:

        logger.error("BOT_TOKEN or CHAT_ID not found")

        return False

    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )

    try:

        response = session.post(

            url,

            data={

                "chat_id": CHAT_ID,

                "text": text,

                "parse_mode": parse_mode,

                "disable_web_page_preview": disable_preview

            },

            timeout=session.request_timeout

        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):

            logger.error(result)

            return False

        return True

    except Exception as e:

        logger.exception(e)

        return False
