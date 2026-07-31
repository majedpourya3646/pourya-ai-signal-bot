import time
import json
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



    def _generate_sign(
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


        prepared_string = (

            method.upper()

            +

            path

            +

            body

            +

            timestamp

        )


        signature = hmac.new(

            self.secret_key.encode("latin-1"),

            prepared_string.encode("latin-1"),

            hashlib.sha256

        ).hexdigest().lower()



        logger.info(
            f"COINEX SIGN STRING {prepared_string}"
        )


        return signature, timestamp




    def _request(
        self,
        method,
        path,
        params=None,
        body=None,
        private=False
    ):


        params = params or {}

        body = body or {}


        json_body = ""


        if method.upper() != "GET":

            json_body = json.dumps(

                body,

                separators=(
                    ",",
                    ":"
                ),

                ensure_ascii=False

            )



        headers = {

            "Content-Type":

            "application/json"

        }



        if private:


            if not self.api_key or not self.secret_key:


                return {

                    "code": -1,

                    "message":

                    "API KEY EMPTY"

                }



            sign, timestamp = self._generate_sign(

                method,

                path,

                json_body,

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

                    data=json_body,

                    headers=headers,

                    timeout=REQUEST_TIMEOUT

                )



            logger.info(

                f"COINEX URL {response.url}"

            )


            logger.info(

                f"STATUS {response.status_code}"

            )



            result = response.json()



            logger.info(

                f"COINEX RESPONSE {result}"

            )


            return result



        except Exception as e:


            logger.exception(e)


            return {

                "code":

                -1,

                "message":

                str(e)

            }




    def get_kline(
        self,
        market,
        period,
        limit=300
    ):


        return self._request(

            "GET",

            "/futures/kline",

            params={

                "market":

                market,


                "period":

                period,


                "limit":

                limit

            }

        )




    def get_balance(self):


        return self._request(

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


        body = {


            "market":

            market,


            "market_type":

            "FUTURES",


            "side":

            side.lower(),


            "type":

            order_type,


            "amount":

            str(amount)

        }



        return self._request(

            "POST",

            "/futures/order",

            body=body,

            private=True

        )




    def cancel_order(
        self,
        order_id,
        market
    ):


        body = {


            "market":

            market,


            "order_id":

            order_id

        }



        return self._request(

            "POST",

            "/futures/cancel-order",

            body=body,

            private=True

        )




coinex = CoinExAPI()
