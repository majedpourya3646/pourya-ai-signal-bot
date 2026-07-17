import time
import json
import hmac
import hashlib
import requests

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY,
)

from core.session import session
from core.logger import logger


class CoinExTrade:

    def __init__(self):
        self.base_url = BASE_URL


    def _sign(
        self,
        method,
        path,
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
        )

        prepared = (
            method
            +
            path
            +
            body
            +
            timestamp
        )

        sign = hmac.new(
            COINEX_SECRET_KEY.encode(),
            prepared.encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            "X-COINEX-KEY": COINEX_API_KEY,
            "X-COINEX-SIGN": sign,
            "X-COINEX-TIMESTAMP": timestamp
        }


    def request(
        self,
        method,
        path,
        params=None
    ):

        url = self.base_url + path

        body = ""

        if params:
            body = json.dumps(
                params,
                separators=(",", ":")
            )


        headers = self._sign(
            method,
            path,
            body
        )


        try:

            if method == "POST":

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
                f"CoinEx Trade Response: {response.text}"
            )


            return response.json()


        except Exception as e:

            logger.exception(e)

            return None



    # ==========================
    # Open Futures Order
    # ==========================

    def open_order(
        self,
        market,
        side,
        amount,
        price=None,
        leverage=10
    ):

        path = "/futures/order"


        params = {

            "market": market,

            "side": side,

            "type": "limit" if price else "market",

            "amount": str(amount),

            "leverage": str(leverage)

        }


        if price:

            params["price"] = str(price)


        return self.request(
            "POST",
            path,
            params
        )



    # ==========================
    # Close Position
    # ==========================

    def close_position(
        self,
        market,
        side,
        amount
    ):

        path = "/futures/order"


        params = {

            "market": market,

            "side": side,

            "type": "market",

            "amount": str(amount),

            "reduce_only": True

        }


        return self.request(
            "POST",
            path,
            params
        )



    # ==========================
    # Balance
    # ==========================

    def get_balance(self):

        return self.request(
            "GET",
            "/assets/futures/balance"
        )



coinex_trade = CoinExTrade()
