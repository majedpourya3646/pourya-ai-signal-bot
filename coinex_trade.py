import time
import hmac
import hashlib
import json

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY
)

from core.session import session
from core.logger import logger


class CoinExTrade:

    def __init__(self):
        self.base_url = BASE_URL


    def sign(
        self,
        method,
        path,
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
        )

        message = (
            method
            + path
            + body
            + timestamp
        )

        signature = hmac.new(
            COINEX_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()


        return {
            "X-COINEX-KEY": COINEX_API_KEY,
            "X-COINEX-SIGN": signature,
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


        headers = self.sign(
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
                f"ORDER RESPONSE: {response.text}"
            )

            return response.json()


        except Exception as e:

            logger.exception(e)

            return None



    # ======================
    # OPEN LONG
    # ======================

    def open_long(
        self,
        symbol,
        amount,
        leverage=10
    ):

        params = {

            "market": symbol,

            "side": "buy",

            "type": "market",

            "amount": str(amount),

            "leverage": str(leverage)

        }


        return self.request(
            "POST",
            "/futures/order",
            params
        )



    # ======================
    # OPEN SHORT
    # ======================

    def open_short(
        self,
        symbol,
        amount,
        leverage=10
    ):

        params = {

            "market": symbol,

            "side": "sell",

            "type": "market",

            "amount": str(amount),

            "leverage": str(leverage)

        }


        return self.request(
            "POST",
            "/futures/order",
            params
        )



    # ======================
    # CLOSE
    # ======================

    def close_position(
        self,
        symbol,
        side,
        amount
    ):

        params = {

            "market": symbol,

            "side": side,

            "type": "market",

            "amount": str(amount),

            "reduce_only": True

        }


        return self.request(
            "POST",
            "/futures/order",
            params
        )



    def get_balance(self):

        return self.request(
            "GET",
            "/assets/futures/balance"
        )



coinex_trade = CoinExTrade()
