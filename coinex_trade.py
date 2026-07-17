import os
import time
import hmac
import hashlib
from urllib.parse import urlencode

from config import BASE_URL, PAPER_TRADING
from core.session import session
from core.logger import logger


class CoinExTrade:


    def __init__(self):

        self.base_url = BASE_URL.rstrip("/")

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
        params=None,
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
        )


        query = ""


        if method.upper() == "GET" and params:

            query = "?" + urlencode(
                sorted(params.items())
            )


        sign_string = (
            method.upper()
            +
            path
            +
            query
            +
            body
            +
            timestamp
        )


        sign = hmac.new(
            self.secret_key.encode(),
            sign_string.encode(),
            hashlib.sha256
        ).hexdigest().lower()


        return sign, timestamp



    def request(
        self,
        method,
        path,
        params=None
    ):


        url = self.base_url + path


        headers = {

            "Content-Type": "application/json",

            "X-COINEX-KEY": self.api_key

        }


        sign, timestamp = self.create_signature(

            method,

            "/v2" + path,

            params

        )


        headers.update({

            "X-COINEX-SIGN": sign,

            "X-COINEX-TIMESTAMP": timestamp

        })



        try:


            if method.upper() == "POST":

                response = session.post(

                    url,

                    json=params,

                    headers=headers,

                    timeout=session.timeout

                )

            else:

                response = session.get(

                    url,

                    params=params,

                    headers=headers,

                    timeout=session.timeout

                )


            logger.info(
                f"TRADE URL: {response.url}"
            )


            logger.info(
                response.text[:500]
            )


            return response.json()


        except Exception as e:

            logger.exception(e)

            return None




    def open_long(
        self,
        market,
        amount
    ):


        if PAPER_TRADING:


            logger.info(
                f"Paper BUY {market} amount={amount}"
            )


            return {

                "paper": True,

                "market": market,

                "amount": amount

            }


        params = {

            "market": market,

            "side": "buy",

            "type": "market",

            "amount": amount

        }


        return self.request(

            "POST",

            "/futures/order",

            params

        )





    def open_short(
        self,
        market,
        amount
    ):


        if PAPER_TRADING:


            logger.info(
                f"Paper SHORT {market} amount={amount}"
            )


            return {

                "paper": True,

                "market": market,

                "amount": amount

            }



        params = {

            "market": market,

            "side": "sell",

            "type": "market",

            "amount": amount

        }


        return self.request(

            "POST",

            "/futures/order",

            params

        )





    def close_position(
        self,
        market
    ):


        if PAPER_TRADING:


            logger.info(
                f"Paper CLOSE {market}"
            )


            return True



        params = {

            "market": market

        }


        return self.request(

            "POST",

            "/futures/close-position",

            params

        )




coinex_trade = CoinExTrade()
