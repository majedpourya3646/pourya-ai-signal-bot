# coinex_trade.py

import time
import json
import hmac
import hashlib

import requests

from core.logger import logger

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY,
    REQUEST_TIMEOUT,
    MARKET_TYPE
)





class CoinExTrade:

    def __init__(self):

        self.base_url = BASE_URL

        self.api_key = COINEX_API_KEY

        self.secret = COINEX_SECRET_KEY






    def _sign(
        self,
        method,
        path,
        body=""
    ):

        try:


            timestamp = str(

                int(

                    time.time()

                    *

                    1000

                )

            )



            prepared = (

                method.upper()

                +

                path

                +

                body

                +

                timestamp

            )



            signature = hmac.new(

                self.secret.encode(),

                prepared.encode(),

                hashlib.sha256

            ).hexdigest()



            return {

                "X-COINEX-KEY":

                    self.api_key,


                "X-COINEX-SIGN":

                    signature,


                "X-COINEX-TIMESTAMP":

                    timestamp,


                "Content-Type":

                    "application/json"

            }



        except Exception as e:


            logger.exception(e)


            return {}








    def request(
        self,
        method,
        path,
        payload=None
    ):

        try:


            body = ""



            if payload:

                body = json.dumps(

                    payload,

                    separators=(

                        ",",

                        ":"

                    )

                )





            headers = self._sign(

                method,

                path,

                body

            )



            url = self.base_url + path





            response = requests.request(

                method,

                url,

                headers=headers,

                data=body,

                timeout=REQUEST_TIMEOUT

            )



            data = response.json()



            if data.get(

                "code"

            ) != 0:


                logger.error(

                    f"COINEX ERROR {data}"

                )


                return None





            return data.get(

                "data"

            )



        except Exception as e:


            logger.exception(e)


            return None







    def create_order(
        self,
        symbol,
        side,
        quantity,
        leverage=1
    ):

        try:


            path = "/futures/order"



            payload = {


                "market":

                    symbol,


                "side":

                    side.lower(),



                "type":

                    "market",



                "amount":

                    str(quantity),



                "leverage":

                    leverage

            }





            return self.request(

                "POST",

                path,

                payload

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

                if side == "BUY"

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


            if MARKET_TYPE == "FUTURES":


                path = "/futures/balance"



            else:


                path = "/assets/spot/balance"





            return self.request(

                "GET",

                path

            )



        except Exception as e:


            logger.exception(e)


            return None








coinex_trade = CoinExTrade()
