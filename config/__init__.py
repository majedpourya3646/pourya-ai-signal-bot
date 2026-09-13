from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)


# ============================================================
# BOT INFORMATION
# ============================================================

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
# MT5 CONNECTION
# ============================================================

MT5_LOGIN = _env_int("MT5_LOGIN", 0)
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "").strip()
MT5_SERVER = os.getenv("MT5_SERVER", "OtetGroup-MT5").strip()

MT5_TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    r"C:\MT5-Pourya\terminal64.exe",
).strip()

MT5_PORTABLE = _env_bool("MT5_PORTABLE", True)

MT5_TIMEOUT = _env_int(
    "MT5_TIMEOUT",
    60000,
)


# ============================================================
# BROKER / MARKET
# ============================================================

BROKER = "MT5"
MARKET_TYPE = "FOREX"

TRADING_SYMBOL = "XAUUSD.su"

SYMBOLS = [
    TRADING_SYMBOL,
]

TIMEFRAME = "M15"

TIMEFRAMES = [
    "M15",
    "H1",
    "H4",
]


# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()


# ============================================================
# TRADING MODE / SAFETY
# ============================================================

AUTO_TRADE = True

# MUST remain True until final explicit approval.
PAPER_TRADING = True

# MUST remain False until all safety gates pass and user explicitly
# approves controlled live trading.
ALLOW_LIVE_TRADING = False

AUTO_CLOSE = True

ORDER_TYPE = "market"
POSITION_SIDE = "both"
MARGIN_MODE = "broker"

# Broker account itself is currently 1:100.
LEVERAGE = 100


# ============================================================
# POSITION LIMITS
# ============================================================

MAX_OPEN_TRADES = 5

# Project-level hard limits.
MIN_PROJECT_LOT = 0.01
MAX_PROJECT_LOT = 0.03

DEFAULT_LOT = 0.01

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# ============================================================
# RISK MANAGEMENT
# ============================================================

RISK_PER_TRADE = 1.0

RISK_REWARD = 2.0
MIN_RISK_REWARD = 2.0

# Maximum permitted daily loss relative to the actual account
# risk baseline. This is NOT based on INITIAL_BALANCE.
MAX_DAILY_LOSS_PERCENT = 5.0


# ============================================================
# SL / TP
# ============================================================

DEFAULT_TP = 5.0
DEFAULT_SL = 2.0

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
# SIGNAL ENGINE
# ============================================================

MIN_CONFIDENCE = 60

USE_MULTI_TIMEFRAME = True

USE_VOLUME_FILTER = True

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_ATR_FILTER = True


# ============================================================
# SCHEDULER
# ============================================================

TRADING_INTERVAL = 60

SCHEDULER_INTERVAL = 60

SCHEDULER_MODE = "RUNNING"


# ============================================================
# NETWORK / RETRY
# ============================================================

REQUEST_TIMEOUT = 20

MAX_RETRIES = 3


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

# Kept only for backward compatibility with older modules.
# Risk calculations for the real account MUST use live MT5
# account equity/balance instead of this value.
INITIAL_BALANCE = 100.0


# ============================================================
# ENV FILE
# ============================================================

ENV_FILE_PATH = str(ENV_FILE)


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

# These assertions intentionally prevent accidental configuration
# drift during the controlled 7-day test.

assert TRADING_SYMBOL == "XAUUSD.su"

assert MIN_PROJECT_LOT > 0

assert MAX_PROJECT_LOT >= MIN_PROJECT_LOT

assert DEFAULT_LOT >= MIN_PROJECT_LOT

assert DEFAULT_LOT <= MAX_PROJECT_LOT

assert MAX_OPEN_TRADES == 5

assert MAX_DAILY_LOSS_PERCENT > 0

assert MAX_DAILY_LOSS_PERCENT <= 5.0

assert LEVERAGE == 100
