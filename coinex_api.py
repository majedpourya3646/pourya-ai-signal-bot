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


class CoinExAPI:

    def __init__(self):
        self.api_key = COINEX_API_KEY
        self.secret_key = COINEX_SECRET_KEY


    def _headers(self, method, path, body=""):

        timestamp = str(int(time.time() * 1000))

        message = (
            method.upper()
            + path
            + body
            + timestamp
        )

        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().lower()

        return {
            "X-COINEX-KEY": self.api_key,
            "X-COINEX-SIGN": signature,
            "X-COINEX-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }



    def _request(
        self,
        method,
        path,
        payload=None
    ):

        url = BASE_URL + path

        body = ""

        if payload:

            body = json.dumps(
                payload,
                separators=(",", ":")
            )


        try:

            response = session.request(
                method=method,
                url=url,
                json=payload,
                headers=self._headers(
                    method,
                    path,
                    body
                ),
                timeout=session.request_timeout
            )


            # DEBUG
            print("==============================")
            print("URL:", url)
            print("STATUS:", response.status_code)
            print("RESPONSE:")
            print(response.text)
            print("==============================")


            result = response.json()


            if result.get("code") != 0:

                logger.error(result)

                return None


            return result



        except Exception as e:

            logger.exception(e)

            return None




    # =========================
    # BALANCE
    # =========================

    def get_balance(self):

        return self.get_futures_balance()



    def get_futures_balance(self):

        return self._request(
            "GET",
            "/v2/assets/futures/balance"
        )



    # =========================
    # POSITIONS
    # =========================

    def get_futures_positions(self):

        return self._request(
            "GET",
            "/v2/futures/pending-position"
        )



    # =========================
    # ORDER
    # =========================

    def create_futures_order(
        self,
        market,
        side,
        amount,
        order_type="market"
    ):

        return self._request(
            "POST",
            "/v2/futures/order",
            {
                "market": market,
                "market_type": "FUTURES",
                "side": side,
                "type": order_type,
                "amount": str(amount)
            }
        )



coinex = CoinExAPI()
