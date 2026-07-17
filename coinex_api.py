import os
import time
import json
import hmac
import hashlib

from config import BASE_URL
from core.session import session
from core.logger import logger


class CoinExAPI:

    def __init__(self):
        self.base_url = BASE_URL

        self.api_key = os.getenv(
            "COINEX_API_KEY"
        )

        self.secret_key = os.getenv(
            "COINEX_SECRET_KEY"
        )


    def create_signature(
        self,
        method,
        path,
        body="",
        timestamp=None
    ):

        if timestamp is None:
            timestamp = str(
                int(time.time() * 1000)
            )


        message = (
            method.upper()
            + path
            + body
            + timestamp
        )


        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
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
                        "Missing CoinEx API keys"
                    )


                sign, timestamp = self.create_signature(
                    method,
                    path,
                    body
                )


                headers.update({

                    "X-COINEX-KEY": self.api_key,

                    "X-COINEX-SIGN": sign,

                    "X-COINEX-TIMESTAMP": timestamp,

                    "X-COINEX-WINDOWTIME": "5000"

                })



            if method.upper() == "GET":

                response = session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=session.timeout
                )


            elif method.upper() == "POST":

                response = session.post(
                    url,
                    data=body,
                    headers=headers,
                    timeout=session.timeout
                )


            else:
                raise Exception(
                    "Unsupported method"
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




    # ==========================
    # SPOT MARKET DATA
    # ==========================

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



    # ==========================
    # FUTURES BALANCE
    # ==========================

    def get_futures_balance(self):

        return self._request(
            "GET",
            "/assets/futures/balance",
            private=True
        )



coinex = CoinExAPI()
