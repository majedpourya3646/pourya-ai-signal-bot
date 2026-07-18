import os
import json
import time
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
            + request_path
            + body
            + timestamp
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
        body=None,
        private=False
    ):

        params = params or {}

        body = body or {}

        query = urlencode(
            sorted(params.items())
        )

        json_body = ""

        if method.upper() != "GET":
            json_body = json.dumps(
                body,
                separators=(",", ":")
            )

        headers = {
            "Content-Type": "application/json"
        }

        if private:

            sign, timestamp = self._sign(
                method,
                "/v2" + path,
                query,
                json_body
            )

            headers.update({

                "X-COINEX-KEY": self.api_key,

                "X-COINEX-SIGN": sign,

                "X-COINEX-TIMESTAMP": timestamp

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
                f"URL: {response.url}"
            )

            logger.info(
                f"STATUS: {response.status_code}"
            )

            logger.info(
                response.text
            )

            if response.status_code != 200:

                return {
                    "code": response.status_code,
                    "message": response.text
                }

            return response.json()

        except Exception as e:

            logger.exception(e)

            return {
                "code": -1,
                "message": str(e)
            }
            
    import json

from config import (
    PAPER_TRADING,
    ORDER_TYPE,
)

from coinex_api import coinex
from core.logger import logger


class CoinExTrade:

    def create_order(
        self,
        market,
        side,
        amount,
        price=None
    ):

        logger.info(f"PAPER_TRADING = {PAPER_TRADING}")

        if PAPER_TRADING:

            logger.info(
                f"PAPER ORDER {side} {market} qty={amount}"
            )

            return {
                "code": 0,
                "message": "Paper Trading",
                "data": {
                    "market": market,
                    "side": side,
                    "amount": amount,
                    "order_id": "PAPER"
                }
            }

        logger.info(
            f"REAL ORDER {side} {market} qty={amount}"
        )

        result = coinex.create_futures_order(
            market=market,
            side=side,
            amount=amount,
            order_type=ORDER_TYPE,
            price=price
        )

        logger.info(
            "ORDER RESULT:"
        )

        logger.info(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            )
        )

        return result


    def open_long(
        self,
        symbol,
        quantity
    ):

        return self.create_order(
            market=symbol,
            side="buy",
            amount=quantity
        )


    def open_short(
        self,
        symbol,
        quantity
    ):

        return self.create_order(
            market=symbol,
            side="sell",
            amount=quantity
        )


    def close_position(
        self,
        symbol,
        side,
        quantity
    ):

        close_side = (
            "sell"
            if side.lower() == "buy"
            else "buy"
        )

        return self.create_order(
            market=symbol,
            side=close_side,
            amount=quantity
        )


coinex_trade = CoinExTrade()   


            
