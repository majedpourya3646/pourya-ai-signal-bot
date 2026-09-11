# config/__init__.py

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


# ============================================================
# BOT
# ============================================================

BOT_NAME = "Pourya Trader AI"

BOT_VERSION = "2.1.0-MT5"


# ============================================================
# META TRADER 5
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


MT5_LOGIN = _env_int(
    "MT5_LOGIN",
    0,
)

MT5_PASSWORD = os.getenv(
    "MT5_PASSWORD",
    "",
)

MT5_SERVER = os.getenv(
    "MT5_SERVER",
    "ePlanet-MT5",
).strip()

BROKER = "MT5"

MARKET_TYPE = "FOREX"


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
# TRADING CONTROL
# ============================================================

AUTO_TRADE = True

PAPER_TRADING = True

ALLOW_LIVE_TRADING = False

AUTO_CLOSE = True

ORDER_TYPE = "market"

POSITION_SIDE = "both"

MARGIN_MODE = "broker"

LEVERAGE = 10


# ============================================================
# RISK MANAGEMENT
# ============================================================

MAX_OPEN_TRADES = 1

RISK_PER_TRADE = 1.0

RISK_REWARD = 2.0

MIN_RISK_REWARD = 2.0

MAX_DAILY_LOSS_PERCENT = 5.0


# ============================================================
# MT5 ORDER SETTINGS
# ============================================================

DEFAULT_LOT = 0.01

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# ============================================================
# DEFAULT TP / SL
# ============================================================

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0


# ============================================================
# PORTFOLIO
# ============================================================

INITIAL_BALANCE = 1000.0


# ============================================================
# SYMBOLS
# ============================================================

SYMBOLS = [
    "XAUUSD.st",
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
# BREAK-EVEN
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
# SAFETY
# ============================================================

# Live automated trading remains explicitly disabled.
# Do not change this until the strategy and paper-trading tests
# have been validated.

PAPER_TRADING = True

ALLOW_LIVE_TRADING = False


# ============================================================
# COMPATIBILITY
# ============================================================

ENV_FILE_PATH = str(ENV_FILE)
