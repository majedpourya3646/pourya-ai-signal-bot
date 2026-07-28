# coinex_api.py

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

            self.secret_key.encode(),

            sign_string.encode(),

            hashlib.sha256

        ).hexdigest().lower()



        return sign, timestamp




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


        query = urlencode(
            sorted(
                params.items()
            )
        )


        json_body = ""


        if method.upper() != "GET":

            json_body = json.dumps(
                body,
                separators=(
                    ",",
                    ":"
                )
            )



        headers = {

            "Content-Type":
            "application/json"

        }



        if private:


            sign, timestamp = self._sign(

                method,

                "/v2" + path,

                query,

                json_body

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



        for attempt in range(3):

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



                data = response.json()



                if response.status_code != 200:

                    return {

                        "code":
                        response.status_code,

                        "message":
                        response.text

                    }



                return data



            except Exception as e:


                logger.warning(
                    f"REQUEST RETRY {attempt+1}/3"
                )


                time.sleep(1)



        return {

            "code":
            -1,

            "message":
            "REQUEST FAILED"

        }




    def get_balance(self):

        return self._request(

            "GET",

            "/assets/futures/balance",

            private=True

        )




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




    def set_leverage(
        self,
        market,
        leverage
    ):


        body = {

            "market":
            market,

            "leverage":
            str(leverage)

        }


        return self._request(

            "POST",

            "/futures/set-leverage",

            body=body,

            private=True

        )




    def create_futures_order(
        self,
        market,
        side,
        amount,
        order_type="market",
        leverage=10
    ):


        side = side.lower()



        self.set_leverage(

            market,

            leverage

        )



        body = {


            "market":

            market,


            "market_type":

            "FUTURES",


            "side":

            side,


            "type":

            order_type,


            "amount":

            str(amount)

        }



        return self._request(

            method="POST",

            path="/futures/order",

            body=body,

            private=True

        )




    def set_stop_loss(
        self,
        market,
        side,
        amount,
        stop_price
    ):


        close_side = (

            "sell"

            if side.lower() == "buy"

            else

            "buy"

        )



        body = {


            "market":

            market,


            "market_type":

            "FUTURES",


            "side":

            close_side,


            "type":

            "stop_market",


            "amount":

            str(amount),


            "stop_price":

            str(stop_price)

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
