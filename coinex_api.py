import time
import json
import hmac
import hashlib
import requests

from config import BASE_URL
from core.session import session
from core.logger import logger


class CoinExAPI:

    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = None
        self.secret_key = None

        import os

        self.api_key = os.getenv("COINEX_API_KEY")
        self.secret_key = os.getenv("COINEX_SECRET_KEY")


    def _signature(self, method, path, body="", timestamp=None):

        if timestamp is None:
            timestamp = str(int(time.time() * 1000))

        message = (
            method.upper()
            + path
            + body
            + timestamp
        )

        sign = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return sign, timestamp


    def _request(self, method, path, params=None, private=False):

        try:

            url = self.base_url + path

            body = ""

            if params:
                body = json.dumps(
                    params,
                    separators=(",", ":")
                )


            headers = {
                "Content-Type": "application/json"
            }


            if private:

                if not self.api_key or not self.secret_key:
                    raise Exception(
                        "CoinEx API keys missing"
                    )

                sign, timestamp = self._signature(
                    method,
                    path,
                    body
                )

                headers.update({
                    "X-COINEX-KEY": self.api_key,
                    "X-COINEX-SIGN": sign,
                    "X-COINEX-TIMESTAMP": timestamp
                })


            if method.upper() == "GET":

                response = session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=session.timeout
                )

            else:

                response = session.post(
                    url,
                    json=params,
                    headers=headers,
                    timeout=session.timeout
                )


            logger.info(
                f"URL: {response.url}"
            )

            logger.info(
                f"STATUS: {response.status_code}"
            )

            logger.info(
                response.text[:500]
            )


            return response.json()


        except Exception as e:

            logger.error(e)
            return None



    # =========================
    # Market Data
    # =========================

    def get_kline(
        self,
        market="BTCUSDT",
        period="15min",
        limit=300
    ):

        path = "/spot/kline"

        params = {
            "market": market,
            "period": period,
            "limit": limit
        }

        return self._request(
            "GET",
            path,
            params
        )


    # =========================
    # Futures Balance
    # =========================

    def get_futures_balance(self):

        path = "/assets/futures/balance"

        return self._request(
            "GET",
            path,
            private=True
        )



coinex = CoinExAPI()
