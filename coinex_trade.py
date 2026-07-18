import time
import json
import hmac
import hashlib

import config

logger.info(f"CONFIG FILE = {config.__file__}")
logger.info(f"PAPER = {config.PAPER_TRADING}")

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



    def sign(
        self,
        method,
        path,
        body=""
    ):

        timestamp = str(
            int(time.time()*1000)
        )

        message = (
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
            message.encode(),
            hashlib.sha256
        ).hexdigest()


        return signature,timestamp



    def create_order(
        self,
        market,
        side,
        amount
    ):
        logger.info(f"PAPER_TRADING = {PAPER_TRADING}")
        logger.info(f"BASE_URL = {self.base_url}")
        logger.info("ENTER create_order()")

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

                    "amount":amount,

                    "order_id":"PAPER"

                }

            }



        path="/v2/futures/order"

        url=self.base_url+path


        payload={

            "market":market,

            "side":side,

            "type":"market",

            "amount":str(amount)

        }


        body=json.dumps(
            payload,
            separators=(",",":")
        )


        sign,timestamp=self.sign(
            "POST",
            path,
            body
        )


        headers={

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

            r=session.post(
                url,
                data=body,
                headers=headers,
                timeout=10
            )


            logger.info(
                "ORDER RESPONSE:"
            )

            logger.info(
                r.text
            )


            return r.json()



        except Exception as e:

            logger.exception(e)

            return None




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




    def close_position(
        self,
        symbol
    ):

        logger.info(
            f"CLOSE REQUEST {symbol}"
        )

        return True




coinex_trade = CoinExTrade()
