import time
import hmac
import hashlib
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("COINEX_API_KEY")
API_SECRET = os.getenv("COINEX_API_SECRET")

BASE_URL = "https://api.coinex.com"


class CoinExFutures:

    def __init__(self):
        self.session = requests.Session()

    def _sign(self, params):

        params["access_id"] = API_KEY
        params["tonce"] = int(time.time() * 1000)

        query = "&".join(
            f"{k}={params[k]}" for k in sorted(params)
        )

        signature = hmac.new(
            API_SECRET.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest().upper()

        params["signature"] = signature

        return params

    def request(self, method, path, params=None):

        if params is None:
            params = {}

        signed = self._sign(params)

        if method == "GET":
            response = self.session.get(
                BASE_URL + path,
                params=signed,
                timeout=20
            )
        else:
            response = self.session.post(
                BASE_URL + path,
                json=signed,
                timeout=20
            )

        return response.json()


coinex = CoinExFutures()
