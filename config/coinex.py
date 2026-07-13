import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.coinex.com/v2"

COINEX_API_KEY = os.getenv("COINEX_API_KEY")

COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

MARKET_TYPE = "FUTURES"

REQUEST_TIMEOUT = 30

MAX_RETRIES = 3
