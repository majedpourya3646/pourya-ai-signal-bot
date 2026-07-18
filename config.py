import os
from dotenv import load_dotenv

load_dotenv()


# ===========================
# CoinEx
# ===========================

BASE_URL = "https://api.coinex.com/v2"

COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")


# ===========================
# Telegram
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")


# ===========================
# Request
# ===========================

REQUEST_TIMEOUT = 20
MAX_RETRIES = 3


# ===========================
# Trading
# ===========================

PAPER_TRADING = True

MARKET_TYPE = "FUTURES"

ORDER_TYPE = "market"

LEVERAGE = 10

RISK_PER_TRADE = 1

MAX_OPEN_TRADES = 3

MIN_CONFIDENCE = 60


# ===========================
# TP / SL
# ===========================

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0


# ===========================
# Balance
# ===========================

INITIAL_BALANCE = 1000.0


# ===========================
# Symbols
# ===========================

SYMBOLS = [

    "BTCUSDT",

    "ETHUSDT",

    "SOLUSDT",

    "XRPUSDT",

    "DOGEUSDT"

]


# ===========================
# TimeFrame
# ===========================

TIMEFRAME = "15"

BOT_NAME = "Pourya Trader AI"
