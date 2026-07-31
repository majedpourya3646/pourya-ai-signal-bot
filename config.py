# config.py

import os

from dotenv import load_dotenv


load_dotenv()



# ===========================
# Application
# ===========================

BOT_NAME = "Pourya Trader AI"

VERSION = "2.0.0"

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "PRODUCTION"
)



# ===========================
# CoinEx API
# ===========================

BASE_URL = "https://api.coinex.com/v2"

COINEX_API_KEY = os.getenv(
    "COINEX_API_KEY",
    ""
)

COINEX_SECRET_KEY = os.getenv(
    "COINEX_SECRET_KEY",
    ""
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
# Request Settings
# ===========================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3



# ===========================
# Market Settings
# ===========================

MARKET_TYPE = "FUTURES"

SUPPORTED_MARKETS = [

    "SPOT",

    "FUTURES"

]



ORDER_TYPE = "market"



# ===========================
# Trading Settings
# ===========================

PAPER_TRADING = True


AUTO_TRADING = True


TRADING_MODE = "AUTO"


LEVERAGE = 10


RISK_PER_TRADE = 1


MAX_OPEN_TRADES = 3


MIN_CONFIDENCE = 65



# ===========================
# Risk Management
# ===========================

MAX_DAILY_LOSS_PERCENT = 5


MIN_RISK_REWARD = 2.0


MAX_POSITION_SIZE_PERCENT = 20



# ===========================
# Take Profit / Stop Loss
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
# Timeframes
# ===========================

TIMEFRAME = "15"


TIMEFRAMES = {

    "15": "15min",

    "60": "1hour",

    "240": "4hour"

}



# ===========================
# Scheduler
# ===========================

SCHEDULER_MODE = "TEST"


TRADING_INTERVAL = 300



# ===========================
# Database
# ===========================

DATABASE_PATH = "data/pourya_trader.db"



# ===========================
# Backup
# ===========================

BACKUP_PATH = "backup"


MAX_BACKUPS = 10



# ===========================
# Notifications
# ===========================

EMAIL_ENABLED = False


SMS_ENABLED = False



# ===========================
# User System
# ===========================

DEFAULT_USER_PROFIT_SHARE = 50


DEFAULT_PLAN = "FREE"
