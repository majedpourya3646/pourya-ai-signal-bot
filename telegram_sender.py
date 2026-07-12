import os
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


session = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[
        500,
        502,
        503,
        504
    ]
)

adapter = HTTPAdapter(
    max_retries=retry
)

session.mount(
    "https://",
    adapter
)


def send_message(
    text,
    parse_mode="HTML",
    disable_preview=True
):

    if not BOT_TOKEN or not CHAT_ID:

        print("Telegram settings missing")

        return False

    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )

    data = {

        "chat_id": CHAT_ID,

        "text": text,

        "parse_mode": parse_mode,

        "disable_web_page_preview": disable_preview

    }

    try:

        response = session.post(
            url,
            data=data,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):

            print(
                "TELEGRAM ERROR:",
                result
            )

            return False

        return True

    except Exception as e:

        print(
            "TELEGRAM ERROR:",
            e
        )

        return False
