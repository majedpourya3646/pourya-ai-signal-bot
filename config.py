# config.py

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
    ""
)


MT5_PATH = os.getenv(
    "MT5_PATH",
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
# Request
# ===========================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3






# ===========================
# Trading
# ===========================

PAPER_TRADING = False


MARKET_TYPE = "FOREX"


ORDER_TYPE = "market"


LEVERAGE = 10



RISK_PER_TRADE = 1



MAX_OPEN_TRADES = 3



MIN_CONFIDENCE = 60






# ===========================
# Lot Management
# ===========================

DEFAULT_LOT = 0.01


MIN_LOT = 0.01


MAX_LOT = 1.0


USE_DYNAMIC_LOT = False






# ===========================
# TP / SL
# ===========================

DEFAULT_TP = 5.0


DEFAULT_SL = 2.0






# ===========================
# Risk
# ===========================

MIN_RISK_REWARD = 2.0


MAX_DAILY_LOSS_PERCENT = 5






# ===========================
# Balance
# ===========================

INITIAL_BALANCE = 1000.0






# ===========================
# User / Profit
# ===========================

DEFAULT_USER_PROFIT_SHARE = 70






# ===========================
# Symbols MT5
# ===========================

SYMBOLS = [

    "BTCUSD",

    "ETHUSD",

    "EURUSD",

    "GBPUSD",

    "XAUUSD"

]






# ===========================
# TimeFrame
# ===========================

TIMEFRAME = "15"


TIMEFRAMES = [

    "15",

    "60",

    "240"

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


BOT_VERSION = "3.0.0 MT5"
