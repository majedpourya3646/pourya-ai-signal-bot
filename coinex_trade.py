# coinex_trade.py

import time
import hmac
import hashlib
import requests

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY,
    MARKET_TYPE,
    PAPER_TRADING,
    REQUEST_TIMEOUT
)

from core.logger import logger





class CoinExTrade:


    def __init__(self):

        self.base_url = BASE_URL

        self.api_key = COINEX_API_KEY

        self.secret = COINEX_SECRET_KEY





    def _sign(
        self,
        payload
    ):

        try:

            message = "&".join(

                [

                    f"{k}={payload[k]}"

                    for k in sorted(payload)

                ]

            )


            return hmac.new(

                self.secret.encode(),

                message.encode(),

                hashlib.sha256

            ).hexdigest()



        except Exception as e:

            logger.exception(e)

            return ""






    def _request(
        self,
        method,
        path,
        params=None
    ):

        try:


            if PAPER_TRADING:

                return {


                    "code":0,


                    "data":{}


                }



            if params is None:

                params = {}



            timestamp = str(

                int(time.time()*1000)

            )



            params["access_id"] = self.api_key

            params["tonce"] = timestamp



            params["signature"] = self._sign(

                params

            )



            url = self.base_url + path



            if method == "GET":

                response = requests.get(

                    url,

                    params=params,

                    timeout=REQUEST_TIMEOUT

                )


            else:

                response = requests.post(

                    url,

                    json=params,

                    timeout=REQUEST_TIMEOUT

                )



            return response.json()



        except Exception as e:


            logger.exception(e)

            return None








    def get_ticker(
        self,
        symbol
    ):

        try:

            url = (

                self.base_url

                +

                "/spot/ticker"

            )



            response = requests.get(

                url,

                params={

                    "market":

                    symbol

                },

                timeout=REQUEST_TIMEOUT

            )



            return response.json()



        except Exception as e:


            logger.exception(e)

            return None








    def create_order(
        self,
        market,
        side,
        amount,
        leverage=10
    ):

        try:


            if PAPER_TRADING:

                return {

                    "code":0,

                    "status":"PAPER",

                    "data":{

                        "order_id":"PAPER",

                        "market":market,

                        "side":side,

                        "amount":amount

                    }

                }



            path = (

                "/futures/order"

                if MARKET_TYPE=="FUTURES"

                else

                "/spot/order"

            )



            params = {


                "market":market,


                "side":side.lower(),


                "amount":amount,


                "type":"market"


            }



            return self._request(

                "POST",

                path,

                params

            )



        except Exception as e:


            logger.exception(e)

            return None









    def close_position(
        self,
        symbol,
        side,
        quantity
    ):

        try:


            close_side = (

                "sell"

                if side.upper()=="BUY"

                else

                "buy"

            )



            return self.create_order(

                symbol,

                close_side,

                quantity

            )



        except Exception as e:


            logger.exception(e)

            return None








    def get_balance(self):

        try:


            return self._request(

                "GET",

                "/assets/spot/balance"

            )



        except Exception as e:


            logger.exception(e)

            return None








    def get_open_positions(self):

        try:


            if PAPER_TRADING:

                return []



            return self._request(

                "GET",

                "/futures/pending-position"

            )



        except Exception as e:


            logger.exception(e)

            return None





coinex_trade = CoinExTrade()
