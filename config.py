import os

# ===========================
# Bot
# ===========================

BOT_NAME = "Pourya Trader AI"

TIMEFRAME = "15m"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]

MIN_CONFIDENCE = 60

# ===========================
# Telegram
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

# ===========================
# CoinEx API
# ===========================

BASE_URL = "https://api.coinex.com"

COINEX_API_KEY = os.getenv("COINEX_API_KEY")

COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

MARKET_TYPE = "FUTURES"

# ===========================
# Trading
# ===========================

LEVERAGE = 10

RISK_REWARD = 2.0

MAX_OPEN_TRADES = 5

RISK_PER_TRADE = 1.0

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0

# ===========================
# Trailing Stop
# ===========================

TRAILING_TRIGGER = 2.0

TRAILING_DISTANCE = 1.0

BREAK_EVEN_TRIGGER = 2.0

# ===========================
# Portfolio
# ===========================

INITIAL_BALANCE = 1000.0

# ===========================
# Paper Trading
# ===========================

PAPER_TRADING = True

AUTO_CLOSE = True

# ===========================
# AI
# ===========================

USE_MULTI_TIMEFRAME = True

USE_VOLUME_FILTER = True

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_ATR_FILTER = True
