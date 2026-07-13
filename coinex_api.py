import time
import hmac
import hashlib
import json

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

    def _headers(self, method, path, body=""):

        timestamp = str(int(time.time() * 1000))

        message = timestamp + method.upper() + path + body

        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

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

        url = BASE_URL + path

        body = ""

        if payload:
            body = json.dumps(
                payload,
                separators=(",", ":")
            )

        try:

            response = session.request(
                method=method,
                url=url,
                json=payload,
                headers=self._headers(
                    method,
                    path,
                    body
                ),
                timeout=session.request_timeout
            )

            response.raise_for_status()

            result = response.json()

            if result.get("code") != 0:

                logger.error(result)

                return None

            return result

        except Exception as e:

            logger.exception(e)

            return None

    def get_balance(self):

        return self._request(
            "GET",
            "/assets/spot/balance"
        )

    def market_buy(
        self,
        market,
        amount
    ):

        return self._request(
            "POST",
            "/spot/order",
            {
                "market": market,
                "market_type": "SPOT",
                "side": "buy",
                "type": "market",
                "amount": str(amount)
            }
        )

    def market_sell(
        self,
        market,
        amount
    ):

        return self._request(
            "POST",
            "/spot/order",
            {
                "market": market,
                "market_type": "SPOT",
                "side": "sell",
                "type": "market",
                "amount": str(amount)
            }
        )


coinex = CoinExAPI()
