import time
import json
import hmac
import hashlib
import requests

from urllib.parse import urlencode

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY
)

from core.session import session
from core.logger import logger


class CoinExAPI:

    def __init__(self):

        self.api_key = COINEX_API_KEY
        self.secret_key = COINEX_SECRET_KEY
        self.base_url = BASE_URL.rstrip("/")

    def _headers(
        self,
        method,
        request_path,
        body=""
    ):

        timestamp = str(int(time.time() * 1000))

        prepared = (
            method.upper()
            + request_path
            + body
            + timestamp
        )

        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            prepared.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().lower()

        return {
            "X-COINEX-KEY": self.api_key,
            "X-COINEX-SIGN": signature,
            "X-COINEX-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }

    def _request(
        self,
        method,
        path,
        payload=None
    ):

        body = ""

        request_path = path

        if method.upper() == "GET" and payload:

            query = urlencode(payload)

            request_path = f"{path}?{query}"

            url = self.base_url + request_path

        else:

            url = self.base_url + path

            if payload is not None:

                body = json.dumps(
                    payload,
                    separators=(",", ":")
                )

        try:

            headers = self._headers(
                method,
                request_path,
                body
            )

            if method.upper() == "GET":

                response = session.get(
                    url,
                    headers=headers,
                    timeout=session.timeout
                )

            else:

                response = session.post(
                    url,
                    headers=headers,
                    data=body if body else None,
                    timeout=session.request_timeout
                )

            print("=" * 60)
            print("URL:", url)
            print("STATUS:", response.status_code)
            print(response.text)
            print("=" * 60)

            response.raise_for_status()

            result = response.json()

            if result.get("code") != 0:
                logger.error(result)
                return None

            return result

        except Exception as e:

            logger.exception(e)

            return None

    # =========================
    # BALANCE
    # =========================

    def get_balance(self):
        return self.get_futures_balance()

    def get_futures_balance(self):
        return self._request(
            "GET",
            "/assets/futures/balance"
        )

    # =========================
    # POSITIONS
    # =========================

    def get_futures_positions(self):
        return self._request(
            "GET",
            "/futures/pending-position"
        )

    # =========================
    # CREATE ORDER
    # =========================

    def create_futures_order(
        self,
        market,
        side,
        amount,
        order_type="market",
        leverage=10
    ):

        payload = {
            "market": market,
            "market_type": "FUTURES",
            "side": side,
            "type": order_type,
            "amount": str(amount),
            "leverage": leverage
        }

        return self._request(
            "POST",
            "/futures/order",
            payload
        )

    # =========================
    # LEVERAGE
    # =========================

    def set_leverage(
        self,
        market,
        leverage
    ):

        payload = {
            "market": market,
            "market_type": "FUTURES",
            "leverage": leverage
        }

        return self._request(
            "POST",
            "/futures/set-leverage",
            payload
        )

    # =========================
    # TP / SL
    # =========================

    def set_tp_sl(
        self,
        market,
        position_id,
        take_profit,
        stop_loss
    ):

        payload = {
            "market": market,
            "position_id": position_id,
            "take_profit": str(take_profit),
            "stop_loss": str(stop_loss)
        }

        return self._request(
            "POST",
            "/futures/set-position-stop",
            payload
        )

    def cancel_order(
        self,
        market,
        order_id
    ):

        return self._request(
            "POST",
            "/futures/cancel-order",
            {
                "market": market,
                "order_id": order_id
            }
        )

    def get_open_orders(
        self,
        market
    ):

        return self._request(
            "GET",
            "/futures/pending-order",
            {
                "market": market
            }
        )


coinex = CoinExAPI()
