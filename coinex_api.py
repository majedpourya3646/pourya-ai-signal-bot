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
        self.base_url = BASE_URL.rstrip("/")
        self.api_key = os.getenv("COINEX_API_KEY")
        self.secret_key = os.getenv("COINEX_SECRET_KEY")


    def create_signature(
        self,
        method,
        request_path,
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
        )


        sign_string = (
            method.upper()
            + request_path
            + body
            + timestamp
        )


        print("================")
        print("SIGN STRING:")
        print(sign_string)
        print("================")


        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().lower()


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


            if method.upper() == "POST" and params:

                body = json.dumps(
                    params,
                    separators=(",", ":")
                )


            headers = {
                "Content-Type": "application/json"
            }



            if private:

                request_path = "/v2" + path


                if method.upper() == "GET" and params:

                    request_path += "?" + urlencode(params)



                sign, timestamp = self.create_signature(
                    method,
                    request_path,
                    body
                )


                headers.update({

                    "X-COINEX-KEY": self.api_key,
                    "X-COINEX-SIGN": sign,
                    "X-COINEX-TIMESTAMP": timestamp,
                    "Authorization": self.api_key

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
