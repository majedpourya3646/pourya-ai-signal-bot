import os
import requests
from dotenv import load_dotenv

load_dotenv()

COINEX_API_KEY = os.getenv("COINEX_API_KEY")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

BASE_URL = "https://api.coinex.com/v2"


session = requests.Session()


def test_connection():
    if not COINEX_API_KEY or not COINEX_SECRET_KEY:
        return {
            "status": "error",
            "message": "API keys not found"
        }

    return {
        "status": "ok",
        "message": "CoinEx API keys loaded"
    }
