import os
import time
import hmac
import hashlib
from urllib.parse import urlencode

from config import BASE_URL
from core.session import session
from core.logger import logger



class CoinExAPI:


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


        if (
            method.upper() == "GET"
            and params
        ):

            query = "?" + urlencode(
                sorted(params.items())
            )


        request_path = path + query


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



            if method.upper() == "GET":


                response = session.get(

                    url,

                    params=params,

                    headers=headers,

                    timeout=session.timeout

                )


            else:


                response = session.post(

                    url,

                    json=params,

                    headers=headers,

                    timeout=session.timeout

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

            return None





    # ===========================
    # Futures Balance
    # ===========================

    def get_futures_balance(self):

        return self._request(

            "GET",

            "/assets/futures/balance",

            private=True

        )





    # ===========================
    # Spot Balance
    # ===========================

    def get_spot_balance(self):

        return self._request(

            "GET",

            "/assets/spot/balance",

            private=True

        )





    # ===========================
    # Compatibility
    # ===========================

    def get_balance(self):

        return self.get_futures_balance()
    # ===========================
    # Set Futures Leverage
    # ===========================

    def set_leverage(self, market, leverage):

        return self._request(
            "POST",
            "/futures/set-leverage",
            params={
                "market": market,
                "leverage": leverage
            },
            private=True
        )


    # ===========================
    # Open Futures Order
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
            "market": market,
            "market_type": "FUTURES",
            "side": side,
            "type": order_type,
            "amount": str(amount)
        }

        if price is not None:
            data["price"] = str(price)

        return self._request(
            "POST",
            "/futures/order",
            params=data,
            private=True
        )


    # ===========================
    # Close Position
    # ===========================

    def close_position(
        self,
        market,
        side,
        amount
    ):

        return self.create_futures_order(
            market=market,
            side=side,
            amount=amount,
            order_type="market"
        )


    # ===========================
    # Open Positions
    # ===========================

    def get_positions(self):

        return self._request(
            "GET",
            "/futures/pending-position",
            private=True
        )


    # ===========================
    # Open Orders
    # ===========================

    def get_open_orders(
        self,
        market=None
    ):

        params = {}

        if market:
            params["market"] = market

        return self._request(
            "GET",
            "/futures/pending-order",
            params=params,
            private=True
        )


    # ===========================
    # Cancel Order
    # ===========================

    def cancel_order(
        self,
        market,
        order_id
    ):

        return self._request(
            "POST",
            "/futures/cancel-order",
            params={
                "market": market,
                "order_id": order_id
            },
            private=True
        )


    # ===========================
    # Market Information
    # ===========================

    def get_market_info(
        self,
        market
    ):

        return self._request(
            "GET",
            "/futures/market",
            params={
                "market": market
            }
        )




coinex = CoinExAPI()
