from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def _env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name, "").strip()

    if not value:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float = 0.0) -> float:
    value = os.getenv(name, "").strip()

    if not value:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# PROJECT
# ============================================================

BOT_NAME = "Pourya Trader AI"
BOT_VERSION = "2.2.0-MT5-SAFE"


# ============================================================
# MT5 ACCOUNT
# ============================================================

MT5_LOGIN = _env_int("MT5_LOGIN", 815143)

MT5_PASSWORD = os.getenv("MT5_PASSWORD", "").strip()

MT5_SERVER = os.getenv(
    "MT5_SERVER",
    "OtetGroup-MT5",
).strip()


# ============================================================
# MT5 TERMINAL
# ============================================================

MT5_TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    r"C:\MT5-Pourya\terminal64.exe",
).strip()

MT5_PORTABLE = os.getenv(
    "MT5_PORTABLE",
    "true",
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

MT5_TIMEOUT = _env_int(
    "MT5_TIMEOUT",
    60000,
)

# Compatibility aliases
MT5_PATH = MT5_TERMINAL_PATH
MT5_PORTABLE_MODE = MT5_PORTABLE
MT5_CONNECTION_TIMEOUT = MT5_TIMEOUT


# ============================================================
# BROKER / MARKET
# ============================================================

BROKER = "MT5"
MARKET_TYPE = "FOREX"

LEVERAGE = 100


# ============================================================
# PILOT SYMBOL
# ============================================================

PILOT_SYMBOL = "XAUUSD.su"

SYMBOLS = [
    PILOT_SYMBOL,
]


# ============================================================
# TIMEFRAMES
# ============================================================

TIMEFRAME = "M15"

TIMEFRAMES = [
    "M15",
    "H1",
    "H4",
]

USE_MULTI_TIMEFRAME = True


# ============================================================
# TRADING MODE / SAFETY
# ============================================================

AUTO_TRADE = True

# VERY IMPORTANT:
# Keep these values unchanged until the final live-trading approval.
PAPER_TRADING = True
ALLOW_LIVE_TRADING = False

AUTO_CLOSE = True

ORDER_TYPE = "market"
POSITION_SIDE = "both"
MARGIN_MODE = "broker"


# ============================================================
# POSITION LIMITS
# ============================================================

MAX_OPEN_TRADES = 5
MAX_PROJECT_POSITIONS = 5


# ============================================================
# PROJECT LOT LIMITS
# ============================================================

MIN_PROJECT_LOT = 0.01
DEFAULT_LOT = 0.01
MAX_PROJECT_LOT = 0.03


# ============================================================
# RISK MANAGEMENT
# ============================================================

RISK_PER_TRADE = 1.0

RISK_REWARD = 2.0
MIN_RISK_REWARD = 2.0

MAX_DAILY_LOSS_PERCENT = 5.0

# Compatibility only.
# Risk calculations MUST NOT use this as the live account balance.
INITIAL_BALANCE = 1000.0


# ============================================================
# MT5 ORDER SETTINGS
# ============================================================

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# ============================================================
# DEFAULT SL / TP
# ============================================================

DEFAULT_TP = 5.0
DEFAULT_SL = 2.0


# ============================================================
# SIGNAL ENGINE
# ============================================================

MIN_CONFIDENCE = 60

USE_VOLUME_FILTER = True
USE_ADX_FILTER = True
USE_RSI_FILTER = True
USE_MACD_FILTER = True
USE_ATR_FILTER = True


# ============================================================
# ATR / AUTOMATIC SL & TP
# ============================================================

ENABLE_AUTO_SL_TP = True

ATR_PERIOD = 14

ATR_SL_MULTIPLIER = 1.5
ATR_TP_MULTIPLIER = 3.0


# ============================================================
# BREAK EVEN
# ============================================================

ENABLE_BREAK_EVEN = True

BREAK_EVEN_TRIGGER_PERCENT = 1.0
BREAK_EVEN_OFFSET_PERCENT = 0.05


# ============================================================
# TRAILING STOP
# ============================================================

ENABLE_TRAILING_STOP = True

TRAILING_START_PERCENT = 1.5
TRAILING_DISTANCE_PERCENT = 0.75


# ============================================================
# SCHEDULER / LOOP
# ============================================================

TRADING_INTERVAL = 60

SCHEDULER_INTERVAL = 60

SCHEDULER_MODE = "RUNNING"


# ============================================================
# REQUEST / RETRY
# ============================================================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3


# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "",
).strip()

CHAT_ID = os.getenv(
    "CHAT_ID",
    "",
).strip()


# ============================================================
# ENV PATH
# ============================================================

ENV_FILE_PATH = str(ENV_FILE)


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "BOT_NAME",
    "BOT_VERSION",

    "PROJECT_ROOT",
    "ENV_FILE",
    "ENV_FILE_PATH",

    "MT5_LOGIN",
    "MT5_PASSWORD",
    "MT5_SERVER",

    "MT5_TERMINAL_PATH",
    "MT5_PORTABLE",
    "MT5_TIMEOUT",

    "MT5_PATH",
    "MT5_PORTABLE_MODE",
    "MT5_CONNECTION_TIMEOUT",

    "BROKER",
    "MARKET_TYPE",
    "LEVERAGE",

    "PILOT_SYMBOL",
    "SYMBOLS",

    "TIMEFRAME",
    "TIMEFRAMES",
    "USE_MULTI_TIMEFRAME",

    "AUTO_TRADE",
    "PAPER_TRADING",
    "ALLOW_LIVE_TRADING",
    "AUTO_CLOSE",

    "ORDER_TYPE",
    "POSITION_SIDE",
    "MARGIN_MODE",

    "MAX_OPEN_TRADES",
    "MAX_PROJECT_POSITIONS",

    "MIN_PROJECT_LOT",
    "DEFAULT_LOT",
    "MAX_PROJECT_LOT",

    "RISK_PER_TRADE",
    "RISK_REWARD",
    "MIN_RISK_REWARD",
    "MAX_DAILY_LOSS_PERCENT",
    "INITIAL_BALANCE",

    "MT5_DEVIATION",
    "MT5_MAGIC_NUMBER",
    "MT5_ORDER_COMMENT",

    "DEFAULT_TP",
    "DEFAULT_SL",

    "MIN_CONFIDENCE",

    "USE_VOLUME_FILTER",
    "USE_ADX_FILTER",
    "USE_RSI_FILTER",
    "USE_MACD_FILTER",
    "USE_ATR_FILTER",

    "ENABLE_AUTO_SL_TP",
    "ATR_PERIOD",
    "ATR_SL_MULTIPLIER",
    "ATR_TP_MULTIPLIER",

    "ENABLE_BREAK_EVEN",
    "BREAK_EVEN_TRIGGER_PERCENT",
    "BREAK_EVEN_OFFSET_PERCENT",

    "ENABLE_TRAILING_STOP",
    "TRAILING_START_PERCENT",
    "TRAILING_DISTANCE_PERCENT",

    "TRADING_INTERVAL",
    "SCHEDULER_INTERVAL",
    "SCHEDULER_MODE",

    "REQUEST_TIMEOUT",
    "MAX_RETRIES",

    "BOT_TOKEN",
    "CHAT_ID",
]
