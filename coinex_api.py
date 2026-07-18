import os
import json
import time
import hmac
import hashlib
from urllib.parse import urlencode

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY,
    REQUEST_TIMEOUT
)

from core.session import session
from core.logger import logger


class CoinExAPI:


    def __init__(self):

        self.base_url = BASE_URL.rstrip("/")

        self.api_key = COINEX_API_KEY

        self.secret_key = COINEX_SECRET_KEY



    def _sign(
        self,
        method,
        path,
        query="",
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
        )


        request_path = path


        if query:

            request_path += "?" + query



        sign_string = (
            method.upper()
            +
            request_path
            +
            body
            +
            timestamp
        )


        sign = hmac.new(
            self.secret_key.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().lower()



        logger.info(
            f"SIGN STRING: {sign_string}"
        )

        logger.info(
            f"SIGN: {sign}"
        )


        return sign, timestamp




    def _request(
        self,
        method,
        path,
        params=None,
        private=False
    ):


        params = params or {}

        query = urlencode(
            sorted(params.items())
        )


        body = ""


        headers = {

            "Content-Type":
            "application/json"

        }



        if private:


            sign, timestamp = self._sign(

                method,

                "/v2" + path,

                query,

                body

            )


            headers.update({

                "X-COINEX-KEY":
                self.api_key,


                "X-COINEX-SIGN":
                sign,


                "X-COINEX-TIMESTAMP":
                timestamp

            })



        url = self.base_url + path



        try:


            if method.upper() == "GET":


                response = session.get(

                    url,

                    params=params,

                    headers=headers,

                    timeout=REQUEST_TIMEOUT

                )


            else:


                response = session.post(

                    url,

                    json=params,

                    headers=headers,

                    timeout=REQUEST_TIMEOUT

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


            return {

                "code":-1,

                "message":str(e)

            }





    # ===========================
    # Balance
    # ===========================

    def get_futures_balance(self):

        return self._request(

            "GET",

            "/assets/futures/balance",

            private=True

        )



    def get_balance(self):

        return self.get_futures_balance()



    # ===========================
    # Futures Order
    # ===========================

    def create_futures_order(
        self,
        market,
        side,
        amount,
        order_type="market",
        price=None
    ):


        data = {

            "market":market,

            "market_type":"FUTURES",

            "side":side,

            "type":order_type,

            "amount":str(amount)

        }



        if price:

            data["price"] = str(price)



        return self._request(

            "POST",

            "/futures/order",

            params=data,

            private=True

        )



coinex = CoinExAPI()
