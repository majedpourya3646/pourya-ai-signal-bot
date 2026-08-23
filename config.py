import os

from dotenv import load_dotenv


load_dotenv()


# ===========================
# MetaTrader 5
# ===========================

MT5_LOGIN = int(
    os.getenv(
        "MT5_LOGIN",
        "0"
    )
)

MT5_PASSWORD = os.getenv(
    "MT5_PASSWORD",
    ""
)

MT5_SERVER = os.getenv(
    "MT5_SERVER",
    "ePlanet-MT5"
)


# ===========================
# Telegram
# ===========================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    ""
)

CHAT_ID = os.getenv(
    "CHAT_ID",
    ""
)


# ===========================
# Request
# ===========================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3


# ===========================
# Trading Platform
# ===========================

BROKER = "MT5"

MARKET_TYPE = "FOREX"

ORDER_TYPE = "market"

PAPER_TRADING = True


# ===========================
# MT5 Order Settings
# ===========================

DEFAULT_LOT = 0.01

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# ===========================
# Risk Management
# ===========================

LEVERAGE = 10

RISK_PER_TRADE = 1

MAX_OPEN_TRADES = 3

MIN_CONFIDENCE = 60

MIN_RISK_REWARD = 2.0

MAX_DAILY_LOSS_PERCENT = 5


# ===========================
# TP / SL
# ===========================

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0

DEFAULT_LOT = 0.01


# ===========================
# Balance
# ===========================

INITIAL_BALANCE = 1000.0


# ===========================
# Profit Sharing
# ===========================

DEFAULT_USER_PROFIT_SHARE = 70


# ===========================
# Symbols MT5
# ===========================

SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "XAUUSD",
    "BTCUSD"
]


# ===========================
# Timeframes
# ===========================

TIMEFRAME = "M15"

TIMEFRAMES = [
    "M15",
    "H1",
    "H4"
]


# ===========================
# Scheduler
# ===========================

SCHEDULER_INTERVAL = 60

SCHEDULER_MODE = "RUNNING"


# ===========================
# Bot
# ===========================

BOT_NAME = "Pourya Trader AI"

BOT_VERSION = "2.1.0-MT5"
