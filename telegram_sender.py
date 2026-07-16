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

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {

        "chat_id": CHAT_ID,

        "text": text,

        "parse_mode": parse_mode,

        "disable_web_page_preview": disable_preview

    }

    try:

        response = session.post(
            url,
            data=payload,
            timeout=session.request_timeout
        )

        if response.status_code != 200:

            logger.error(
                f"Telegram Error {response.status_code}: {response.text}"
            )

            return False

        result = response.json()

        if not result.get("ok"):

            logger.error(result)

            return False

        logger.info("Telegram message sent.")

        return True

    except Exception as e:

        logger.exception(e)

        return False
