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



    def _signature(
        self,
        method,
        request_path,
        body="",
        timestamp=None
    ):

        if timestamp is None:

            timestamp = str(
                int(time.time()*1000)
            )


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

        ).hexdigest()


        logger.info(
            f"SIGN STRING: {sign_string}"
        )

        logger.info(
            f"SIGN: {sign}"
        )


        return sign,timestamp




    def request(
        self,
        method,
        path,
        params=None,
        private=False
    ):


        params = params or {}


        url = self.base_url + path


        body = ""


        headers = {

            "Content-Type":
            "application/json"

        }



        if method.upper() == "POST":

            body = json.dumps(
                params,
                separators=(",",":")
            )



        if private:


            query = ""

            if method.upper()=="GET" and params:

                query = "?" + urlencode(
                    sorted(params.items())
                )


            sign_path = "/v2" + path + query


            sign,timestamp = self._signature(

                method,

                sign_path,

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



        try:


            if method.upper()=="GET":


                r=session.get(

                    url,

                    params=params,

                    headers=headers,

                    timeout=REQUEST_TIMEOUT

                )


            else:


                r=session.post(

                    url,

                    data=body,

                    headers=headers,

                    timeout=REQUEST_TIMEOUT

                )



            logger.info(
                f"URL: {r.url}"
            )


            logger.info(
                f"STATUS: {r.status_code}"
            )


            logger.info(
                r.text
            )



            return r.json()



        except Exception as e:


            logger.exception(e)

            return None





    def get_balance(self):


        return self.request(

            "GET",

            "/assets/futures/balance",

            private=True

        )




    def create_futures_order(
        self,
        market,
        side,
        amount,
        order_type="market"
    ):


        return self.request(

            "POST",

            "/futures/order",

            {

                "market":market,

                "market_type":"FUTURES",

                "side":side,

                "type":order_type,

                "amount":str(amount)

            },

            private=True

        )




coinex = CoinExAPI()
