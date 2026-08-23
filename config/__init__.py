import os


# ==========================================
# Bot
# ==========================================

BOT_NAME = "Pourya Trader AI"

BOT_VERSION = "2.1.0-MT5"


# ==========================================
# MetaTrader 5
# ==========================================

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

BROKER = "MT5"

MARKET_TYPE = "FOREX"


# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    ""
)

CHAT_ID = os.getenv(
    "CHAT_ID",
    ""
)


# ==========================================
# Trading
# ==========================================

AUTO_TRADE = True

PAPER_TRADING = True

AUTO_CLOSE = True

ORDER_TYPE = "market"

POSITION_SIDE = "both"

MARGIN_MODE = "broker"

LEVERAGE = 10

MAX_OPEN_TRADES = 3

RISK_PER_TRADE = 1.0

RISK_REWARD = 2.0

MIN_RISK_REWARD = 2.0

MAX_DAILY_LOSS_PERCENT = 5


# ==========================================
# MT5 Order Settings
# ==========================================

DEFAULT_LOT = 0.01

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# ==========================================
# TP / SL
# ==========================================

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0


# ==========================================
# Portfolio
# ==========================================

INITIAL_BALANCE = 1000.0


# ==========================================
# MT5 Symbols
# ==========================================

SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "XAUUSD",
    "BTCUSD",
]


# ==========================================
# Timeframes
# ==========================================

TIMEFRAME = "M15"

TIMEFRAMES = [
    "M15",
    "H1",
    "H4",
]


# ==========================================
# Network
# ==========================================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3


# ==========================================
# AI Filters
# ==========================================

MIN_CONFIDENCE = 60

USE_MULTI_TIMEFRAME = True

USE_VOLUME_FILTER = True

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_ATR_FILTER = True


# ==========================================
# Scheduler
# ==========================================

SCHEDULER_INTERVAL = 60

SCHEDULER_MODE = "RUNNING"
