import os
BOT_NAME = "Pourya Trader AI"

TIMEFRAME = "15m"

RISK_REWARD = 2

MAX_OPEN_TRADES = 5

MIN_CONFIDENCE = 60

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]

# ===========================
# CoinEx API
# ===========================
BASE_URL = "https://api.coinex.com/v2"
COINEX_API_KEY = ""
COINEX_SECRET_KEY = ""

# Futures
MARKET_TYPE = "FUTURES"

# Risk Management
RISK_PER_TRADE = 2      # درصد سرمایه در هر معامله
LEVERAGE = 10           # اهرم پیش‌فرض

# Default TP/SL
DEFAULT_TP = 5          # درصد
DEFAULT_SL = 2          # درصد

# Trailing Stop
TRAILING_TRIGGER = 2    # شروع تریلینگ بعد از ۲٪ سود
TRAILING_DISTANCE = 1   # فاصله تریلینگ

# Break Even
BREAK_EVEN_TRIGGER = 2  # انتقال استاپ به نقطه ورود
