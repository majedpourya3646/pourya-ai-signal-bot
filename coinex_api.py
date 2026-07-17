import os
import time
import hmac
import hashlib
from urllib.parse import urlencode

from config import BASE_URL
from core.session import session
from core.logger import logger


class CoinExAPI:

    def __init__(self):
        self.base_url = BASE_URL.rstrip("/")
        self.api_key = os.getenv("COINEX_API_KEY")
        self.secret_key = os.getenv("COINEX_SECRET_KEY")

    def create_signature(
        self,
        method,
        path,
        params=None,
        body=""
    ):

        timestamp = str(int(time.time() * 1000))

        request_path = path

        if method.upper() == "GET" and params:
            request_path += "?" + urlencode(params)

        sign_string = (
            method.upper()
            + request_path
            + body
            + timestamp
        )

        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return signature, timestamp


    def _request(
        self,
        method,
        path,
        params=None,
        private=False
    ):

        try:

            url = self.base_url + path

            headers = {
                "Content-Type": "application/json"
            }

            body = ""

            if private:

                if not self.api_key or not self.secret_key:
                    raise Exception(
                        "CoinEx API keys are missing"
                    )

                sign, timestamp = self.create_signature(
                    method,
                    path,
                    params,
                    body
                )

                headers.update({
                    "X-COINEX-KEY": self.api_key,
                    "X-COINEX-SIGN": sign,
                    "X-COINEX-TIMESTAMP": timestamp
                })


            timeout = getattr(
                session,
                "timeout",
                15
            )


            if method.upper() == "GET":

                response = session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )

            else:

                response = session.post(
                    url,
                    json=params,
                    headers=headers,
                    timeout=timeout
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

            logger.exception(e)
            return None



    # ===========================
    # Futures Balance
    # ===========================

    def get_futures_balance(self):

        return self._request(
            "GET",
            "/assets/futures/balance",
            private=True
        )


    # ===========================
    # Spot Balance
    # ===========================

    def get_spot_balance(self):

        return self._request(
            "GET",
            "/assets/spot/balance",
            private=True
        )


    # ===========================
    # Compatibility
    # ===========================

    def get_balance(self):

        return self.get_futures_balance()



coinex = CoinExAPI()
