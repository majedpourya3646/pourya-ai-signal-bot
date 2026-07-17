import time
import json
import hmac
import hashlib

from config import (
    BASE_URL,
    COINEX_API_KEY,
    COINEX_SECRET_KEY,
    PAPER_TRADING
)

from core.session import session
from core.logger import logger


class CoinExTrade:


    def __init__(self):

        self.base_url = BASE_URL

        self.api_key = COINEX_API_KEY

        self.secret_key = COINEX_SECRET_KEY



    # =========================
    # Signature
    # =========================

    def sign(
        self,
        method,
        path,
        body=""
    ):

        timestamp = str(
            int(time.time() * 1000)
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
            self.secret_key.encode(),
            prepared.encode(),
            hashlib.sha256
        ).hexdigest()


        return signature, timestamp




    # =========================
    # Futures Order
    # =========================

    def create_order(
        self,
        market,
        side,
        amount,
        price=None
    ):


        if PAPER_TRADING:

            logger.info(
                f"PAPER ORDER {side} {market} qty={amount}"
            )


            return {

                "code":0,

                "message":"Paper Trading",

                "data":{

                    "market":market,

                    "side":side,

                    "amount":amount

                }

            }



        path = "/v2/futures/order"


        url = self.base_url + path


        body_data = {

            "market": market,

            "side": side,

            "type": "market",

            "amount": str(amount)

        }



        body = json.dumps(
            body_data,
            separators=(",",":")
        )



        sign, timestamp = self.sign(
            "POST",
            path,
            body
        )



        headers = {

            "X-COINEX-KEY":
                self.api_key,

            "X-COINEX-SIGN":
                sign,

            "X-COINEX-TIMESTAMP":
                timestamp,

            "Content-Type":
                "application/json"

        }



        try:


            response = session.post(

                url,

                data=body,

                headers=headers,

                timeout=10

            )



            logger.info(
                f"ORDER STATUS: {response.status_code}"
            )


            logger.info(
                response.text
            )



            return response.json()



        except Exception as e:


            logger.exception(e)

            return None




    # =========================
    # Long Position
    # =========================

    def open_long(
        self,
        symbol,
        quantity
    ):


        return self.create_order(

            symbol,

            "buy",

            quantity

        )



    # =========================
    # Short Position
    # =========================

    def open_short(
        self,
        symbol,
        quantity
    ):


        return self.create_order(

            symbol,

            "sell",

            quantity

        )



    # =========================
    # Close Position
    # =========================

    def close_position(
        self,
        symbol
    ):


        logger.info(
            f"Close position {symbol}"
        )


        return True




coinex_trade = CoinExTrade()
