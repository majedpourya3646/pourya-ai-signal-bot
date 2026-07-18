import os

# ==========================================
# Bot
# ==========================================

BOT_NAME = "Pourya Trader AI"

TIMEFRAME = "15m"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
]

MIN_CONFIDENCE = 60


# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")


# ==========================================
# CoinEx
# ==========================================

BASE_URL = "https://api.coinex.com/v2"

COINEX_API_KEY = os.getenv("COINEX_API_KEY")

COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

MARKET_TYPE = "FUTURES"


# ==========================================
# Trading
# ==========================================

AUTO_TRADE = True

PAPER_TRADING = False

AUTO_CLOSE = True

ORDER_TYPE = "market"

POSITION_SIDE = "long"

MARGIN_MODE = "isolated"

LEVERAGE = 10

MAX_OPEN_TRADES = 3

RISK_PER_TRADE = 1.0

RISK_REWARD = 2.0

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0

MAX_POSITION_SIZE = 50

MIN_ORDER_VALUE = 5


# ==========================================
# Portfolio
# ==========================================

INITIAL_BALANCE = 1000.0


# ==========================================
# Network
# ==========================================

REQUEST_TIMEOUT = 15

MAX_RETRIES = 3


# ==========================================
# AI Filters
# ==========================================

USE_MULTI_TIMEFRAME = True

USE_VOLUME_FILTER = True

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_ATR_FILTER = True
