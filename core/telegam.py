# core/telegram.py

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import BOT_TOKEN, CHAT_ID
from core.logger import logger


TELEGRAM_API = "https://api.telegram.org"


def is_configured() -> bool:
    return bool(BOT_TOKEN and str(BOT_TOKEN).strip())


def _api_request(
    method: str,
    params: dict[str, Any] | None = None,
    timeout: int = 15,
) -> dict[str, Any] | None:

    if not is_configured():
        logger.warning("Telegram is not configured.")
        return None

    url = f"{TELEGRAM_API}/bot{BOT_TOKEN}/{method}"

    try:
        data = None

        if params:
            data = urlencode(
                {
                    key: value
                    for key, value in params.items()
                    if value is not None
                }
            ).encode("utf-8")

        request = Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Pourya-Trader-AI",
            },
            method="POST" if data else "GET",
        )

        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")

        result = json.loads(raw)

        if not result.get("ok", False):
            logger.error(
                "Telegram API error | method=%s | description=%s",
                method,
                result.get("description"),
            )
            return None

        return result

    except Exception as exc:
        logger.exception(
            "Telegram request failed | method=%s | error=%s",
            method,
            exc,
        )
        return None


def send_message(
    text: str,
    chat_id: str | int | None = None,
    parse_mode: str | None = None,
    disable_web_page_preview: bool = True,
) -> bool:

    if not text:
        return False

    target_chat_id = chat_id or CHAT_ID

    if not target_chat_id:
        logger.warning("Telegram CHAT_ID is not configured.")
        return False

    params: dict[str, Any] = {
        "chat_id": target_chat_id,
        "text": str(text),
        "disable_web_page_preview": disable_web_page_preview,
    }

    if parse_mode:
        params["parse_mode"] = parse_mode

    result = _api_request(
        "sendMessage",
        params,
    )

    if result is None:
        return False

    logger.info("Telegram message sent successfully.")
    return True


def send_telegram_message(
    text: str,
    chat_id: str | int | None = None,
) -> bool:
    return send_message(
        text=text,
        chat_id=chat_id,
    )


def notify(
    text: str,
    chat_id: str | int | None = None,
) -> bool:
    return send_message(
        text=text,
        chat_id=chat_id,
    )


def get_me() -> dict[str, Any] | None:
    result = _api_request("getMe")

    if result is None:
        return None

    return result.get("result")


def get_updates(
    offset: int | None = None,
    timeout: int = 10,
) -> list[dict[str, Any]]:

    result = _api_request(
        "getUpdates",
        {
            "offset": offset,
            "timeout": timeout,
        },
        timeout=max(15, timeout + 5),
    )

    if result is None:
        return []

    updates = result.get("result", [])

    if not isinstance(updates, list):
        return []

    return updates


def telegram_status() -> dict[str, Any]:
    configured = is_configured()

    status: dict[str, Any] = {
        "configured": configured,
        "chat_id_configured": bool(CHAT_ID),
        "connected": False,
        "bot": None,
    }

    if not configured:
        return status

    bot = get_me()

    if bot:
        status["connected"] = True
        status["bot"] = {
            "id": bot.get("id"),
            "username": bot.get("username"),
            "first_name": bot.get("first_name"),
        }

    return status


__all__ = [
    "send_message",
    "send_telegram_message",
    "notify",
    "get_me",
    "get_updates",
    "is_configured",
    "telegram_status",
]
