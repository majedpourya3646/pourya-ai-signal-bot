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


        if method.upper() == "GET" and params:

            query = urlencode(params)

            request_path += "?" + query


        sign_string = (
            method.upper()
            + request_path
            + body
            + timestamp
        )


        print("================")
        print("SIGN STRING:")
        print(sign_string)

        print("API KEY LENGTH:", len(self.api_key))
        print("SECRET LENGTH:", len(self.secret_key))
        print("SECRET START:", self.secret_key[:4])

        print("================")


        signature = hmac.new(
            self.secret_key.encode("latin-1"),
            sign_string.encode("latin-1"),
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


            headers = {
                "Content-Type": "application/json"
            }


            if private:

                sign, timestamp = self.create_signature(
                    method,
                    "/v2" + path,
                    params,
                    body
                )


                headers.update({

                    "X-COINEX-KEY": self.api_key,

                    "X-COINEX-SIGN": sign,

                    "X-COINEX-TIMESTAMP": timestamp

                })


            response = session.get(
                url,
                params=params,
                headers=headers,
                timeout=session.timeout
            )


            logger.info(
                f"URL: {response.url}"
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



coinex = CoinExAPI()
