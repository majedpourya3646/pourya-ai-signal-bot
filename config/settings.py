import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "Pourya Trader AI"

TIMEFRAME = "15m"

MIN_CONFIDENCE = 60

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
]

REQUEST_TIMEOUT = 30

MAX_RETRIES = 3

RETRY_DELAY = 2

LOG_LEVEL = "INFO"

DRY_RUN = True

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")
