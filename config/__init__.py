# config/__init__.py

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# PROJECT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


BOT_NAME = "Pourya Trader AI"
BOT_VERSION = "2.1.0-MT5"


# ============================================================
# ENV HELPERS
# ============================================================

def _env_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float = 0.0) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# ============================================================
# MT5 ACCOUNT
# ============================================================

MT5_LOGIN = _env_int("MT5_LOGIN", 815143)

MT5_PASSWORD = os.getenv(
    "MT5_PASSWORD",
    "",
).strip()

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

MT5_PORTABLE = _env_bool(
    "MT5_PORTABLE",
    True,
)

MT5_TIMEOUT = _env_int(
    "MT5_TIMEOUT",
    60000,
)

# Compatibility aliases
MT5_PATH = MT5_TERMINAL_PATH
MT5_PORTABLE_MODE = MT5_PORTABLE
MT5_CONNECTION_TIMEOUT = MT5_TIMEOUT


# ============================================================
# BROKER
# ============================================================

BROKER = "MT5"
MARKET_TYPE = "FOREX"


# ============================================================
# PILOT SYMBOL
# ============================================================

PILOT_SYMBOL = "XAUUSD.su"

SYMBOLS = [
    PILOT_SYMBOL,
]


# ============================================================
# TRADING CONTROL
# ============================================================

AUTO_TRADE = True

# IMPORTANT:
# Keep these values unchanged until explicit final approval.
PAPER_TRADING = True
ALLOW_LIVE_TRADING = False

AUTO_CLOSE = True

ORDER_TYPE = "market"

POSITION_SIDE = "both"

MARGIN_MODE = "broker"

LEVERAGE = 100


# ============================================================
# POSITION LIMITS
# ============================================================

MAX_OPEN_TRADES = 5
MAX_PROJECT_POSITIONS = 5

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


# ============================================================
# MT5 ORDER SETTINGS
# ============================================================

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# Compatibility aliases
DEFAULT_MAGIC = MT5_MAGIC_NUMBER
DEFAULT_DEVIATION = MT5_DEVIATION
DEFAULT_COMMENT = MT5_ORDER_COMMENT


# ============================================================
# DEFAULT TP / SL
# ============================================================

DEFAULT_TP = 5.0
DEFAULT_SL = 2.0


# ============================================================
# LEGACY BALANCE
# ============================================================

# Compatibility only.
# NEVER use this as the live risk baseline.
INITIAL_BALANCE = 1000.0


# ============================================================
# TIMEFRAMES
# ============================================================

TIMEFRAME = "M15"

TIMEFRAMES = [
    "M15",
    "H1",
    "H4",
]


# ============================================================
# TRADING LOOP
# ============================================================

TRADING_INTERVAL = 60


# ============================================================
# SCHEDULER
# ============================================================

SCHEDULER_INTERVAL = 60
SCHEDULER_MODE = "RUNNING"


# ============================================================
# NETWORK
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
# AI FILTERS
# ============================================================

MIN_CONFIDENCE = 60

USE_MULTI_TIMEFRAME = True
USE_VOLUME_FILTER = True
USE_ADX_FILTER = True
USE_RSI_FILTER = True
USE_MACD_FILTER = True
USE_ATR_FILTER = True


# ============================================================
# AUTO SL / TP
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
# COMPATIBILITY
# ============================================================

ENV_FILE_PATH = str(ENV_FILE)


# ============================================================
# SAFETY ASSERTIONS
# ============================================================

assert PILOT_SYMBOL == "XAUUSD.su"
assert MIN_PROJECT_LOT == 0.01
assert DEFAULT_LOT >= MIN_PROJECT_LOT
assert MAX_PROJECT_LOT <= 0.03
assert MAX_OPEN_TRADES <= 5
assert MAX_DAILY_LOSS_PERCENT == 5.0

# Fail closed.
# These must remain disabled until explicit approval.
assert PAPER_TRADING is True
assert ALLOW_LIVE_TRADING is False
