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
# BASIC PROJECT INFO
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

MT5_PASSWORD = os.getenv(
    "MT5_PASSWORD",
    "",
).strip()

MT5_SERVER = os.getenv(
    "MT5_SERVER",
    "OtetGroup-MT5",
).strip()

MT5_TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    r"C:\MT5-Pourya\terminal64.exe",
).strip()

MT5_PORTABLE = _env_bool(
    "MT5_PORTABLE",
    True,
)

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
# TRADING MODE / SAFETY
# ============================================================

AUTO_TRADE = True

# IMPORTANT:
# Keep PAPER_TRADING enabled until final live-trading approval.
PAPER_TRADING = True

# IMPORTANT:
# Live trading remains disabled until explicit final approval.
ALLOW_LIVE_TRADING = False

AUTO_CLOSE = True

ORDER_TYPE = "market"

POSITION_SIDE = "both"

MARGIN_MODE = "broker"

LEVERAGE = 100


# ============================================================
# PILOT SYMBOL
# ============================================================

# Current live-test instrument.
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


# ============================================================
# POSITION / RISK LIMITS
# ============================================================

# Maximum number of simultaneous project positions.
MAX_OPEN_TRADES = 5

MAX_PROJECT_POSITIONS = 5

# Broker/project volume limits.
MIN_PROJECT_LOT = 0.01
MAX_PROJECT_LOT = 0.03

DEFAULT_LOT = 0.01

# Percentage of current account equity used by the risk system.
RISK_PER_TRADE = 1.0

RISK_REWARD = 2.0

MIN_RISK_REWARD = 2.0

# Hard daily loss protection.
MAX_DAILY_LOSS_PERCENT = 5.0


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
# LEGACY COMPATIBILITY
# ============================================================

# Kept only for compatibility with older modules.
#
# IMPORTANT:
# Live risk calculations MUST use the current MT5
# account equity/balance and must NOT rely on this value.
INITIAL_BALANCE = 1000.0


# ============================================================
# SIGNAL / INDICATOR SETTINGS
# ============================================================

MIN_CONFIDENCE = 60

USE_MULTI_TIMEFRAME = True

USE_VOLUME_FILTER = True

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_ATR_FILTER = True


# ============================================================
# AUTOMATIC SL / TP
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
# SCHEDULER / TRADING LOOP
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
# ENV FILE
# ============================================================

ENV_FILE_PATH = str(ENV_FILE)
