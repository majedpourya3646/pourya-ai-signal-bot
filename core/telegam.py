# core/telegram.py
# Compatibility layer for the current MT5 project.
# Keeps imports stable while Telegram notification logic remains minimal.

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(
        self,
        token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        if enabled is None:
            enabled_env = os.getenv("TELEGRAM_ENABLED", "true").strip().lower()
            self.enabled = enabled_env not in {"0", "false", "no", "off"}
        else:
            self.enabled = enabled

    def send_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """
        Compatibility method.
        Actual network delivery can be connected by the existing
        telegram_notifier implementation.
        """
        if not self.enabled:
            return False

        if not message:
            return False

        target_chat_id = chat_id or self.chat_id

        if not self.token or not target_chat_id:
            logger.warning(
                "Telegram is enabled but TELEGRAM_BOT_TOKEN or "
                "TELEGRAM_CHAT_ID is not configured."
            )
            return False

        try:
            import requests

            url = f"https://api.telegram.org/bot{self.token}/sendMessage"

            response = requests.post(
                url,
                data={
                    "chat_id": target_chat_id,
                    "text": message,
                },
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

            if not data.get("ok", False):
                logger.error("Telegram API error: %s", data)
                return False

            return True

        except Exception:
            logger.exception("Failed to send Telegram message.")
            return False

    def notify(self, message: str) -> bool:
        return self.send_message(message)

    def send(self, message: str) -> bool:
        return self.send_message(message)


def send_telegram_message(
    message: str,
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> bool:
    notifier = TelegramNotifier(
        token=token,
        chat_id=chat_id,
    )
    return notifier.send_message(message)


def get_telegram_notifier() -> TelegramNotifier:
    return TelegramNotifier()
