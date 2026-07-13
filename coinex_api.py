import time
import hmac
import hashlib
import requests

from config import (
    COINEX_API_KEY,
    COINEX_SECRET_KEY
)

BASE_URL = "https://api.coinex.com/v2"


class CoinExAPI:

    def __init__(self):
        self.api_key = COINEX_API_KEY
        self.secret_key = COINEX_SECRET_KEY

    def _headers(self, method, path, body=""):

        timestamp = str(int(time.time() * 1000))

        message = timestamp + method.upper() + path + body

        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            "X-COINEX-KEY": self.api_key,
            "X-COINEX-SIGN": signature,
            "X-COINEX-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }

    def get_balance(self):

        path = "/assets/spot/balance"

        response = requests.get(
            BASE_URL + path,
            headers=self._headers("GET", path)
        )

        return response.json()

    def market_buy(
        self,
        market,
        amount
    ):

        path = "/spot/order"

        data = {
            "market": market,
            "market_type": "SPOT",
            "side": "buy",
            "type": "market",
            "amount": str(amount)
        }

        response = requests.post(
            BASE_URL + path,
            json=data,
            headers=self._headers(
                "POST",
                path,
                str(data)
            )
        )

        return response.json()

    def market_sell(
        self,
        market,
        amount
    ):

        path = "/spot/order"

        data = {
            "market": market,
            "market_type": "SPOT",
            "side": "sell",
            "type": "market",
            "amount": str(amount)
        }

        response = requests.post(
            BASE_URL + path,
            json=data,
            headers=self._headers(
                "POST",
                path,
                str(data)
            )
        )

        return response.json()


coinex = CoinExAPI()
