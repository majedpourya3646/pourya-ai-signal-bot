import os
import time
import json
import hmac
import hashlib
from urllib.parse import urlencode

from config import BASE_URL
from core.session import session
from core.logger import logger


class CoinExAPI:

    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = os.getenv("COINEX_API_KEY")
        self.secret_key = os.getenv("COINEX_SECRET_KEY")


    def create_signature(
        self,
        method,
        path,
        params=None,
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
        )


        request_path = path


        # برای GET پارامترها باید داخل امضا بیایند
        if method.upper() == "GET" and params:

            query = urlencode(
                params
            )

            request_path += "?" + query


        prepared_str = (
            method.upper()
            + request_path
            + body
            + timestamp
        )


        sign = hmac.new(
            self.secret_key.encode("latin-1"),
            prepared_str.encode("latin-1"),
            hashlib.sha256
        ).hexdigest().lower()


        return sign, timestamp



    def _request(
        self,
        method,
        path,
        params=None,
        private=False
    ):

        try:

            url = self.base_url + path

            body = ""


            headers = {
                "Content-Type": "application/json"
            }


            if private:

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
                    data=body,
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



    def get_futures_balance(self):

        return self._request(
            "GET",
            "/assets/futures/balance",
            private=True
        )



    def get_kline(
        self,
        market="BTCUSDT",
        period="15min",
        limit=300
    ):

        return self._request(
            "GET",
            "/spot/kline",
            {
                "market": market,
                "period": period,
                "limit": limit
            }
        )



coinex = CoinExAPI()
