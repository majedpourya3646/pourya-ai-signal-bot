from __future__ import annotations

import os
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


# ============================================================
# ENV LOADER
# ============================================================

def _load_env_file() -> None:
    if not ENV_FILE.exists():
        return

    try:
        for raw_line in ENV_FILE.read_text(
            encoding="utf-8"
        ).splitlines():

            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            if not key:
                continue

            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in {"'", '"'}
            ):
                value = value[1:-1]

            os.environ.setdefault(key, value)

    except Exception:
        pass


_load_env_file()


# ============================================================
# HELPERS
# ============================================================

def _env_bool(
    name: str,
    default: bool,
) -> bool:

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def _env_int(
    name: str,
    default: int,
) -> int:

    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def _env_float(
    name: str,
    default: float,
) -> float:

    try:
        return float(os.getenv(name, default))
    except Exception:
        return default


def _env_str(
    name: str,
    default: str,
) -> str:

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip()


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "Pourya Trader AI"
APP_VERSION = "0.1"

AUTO_TRADE = _env_bool(
    "AUTO_TRADE",
    True,
)

# IMPORTANT:
# Must remain True until explicit live-trading approval.
PAPER_TRADING = _env_bool(
    "PAPER_TRADING",
    True,
)

# Independent hard live-trading lock.
ALLOW_LIVE_TRADING = _env_bool(
    "ALLOW_LIVE_TRADING",
    False,
)

AUTO_CLOSE = _env_bool(
    "AUTO_CLOSE",
    True,
)


# ============================================================
# PILOT TRADING CONFIG
# ============================================================

SYMBOLS = [
    "XAUUSD.su",
]

PILOT_SYMBOL = "XAUUSD.su"

TIMEFRAME = "M15"

TIMEFRAMES = [
    "M15",
    "H1",
    "H4",
]


# ============================================================
# POSITION LIMITS
# ============================================================

MAX_OPEN_TRADES = 5

DEFAULT_LOT = 0.01

MIN_PROJECT_LOT = 0.01

MAX_PROJECT_LOT = 0.03

LOT_STEP = 0.01

NO_MARTINGALE = True


# ============================================================
# RISK
# ============================================================

RISK_PER_TRADE = 1.0

MAX_DAILY_LOSS_PERCENT = 5.0

RISK_REWARD = 2.0

MIN_RISK_REWARD = 2.0

INITIAL_BALANCE = 1000.0
# Historical/default value only.
# NEVER use this as the real MT5 risk baseline.


# ============================================================
# SIGNAL
# ============================================================

MIN_CONFIDENCE = 60

MTF_ENABLED = True

MTF_MIN_TIMEFRAMES = 3

MTF_MIN_AGREEMENT = 0.0


# ============================================================
# INDICATORS
# ============================================================

EMA_FAST = 20

EMA_SLOW = 50

EMA_TREND = 200

RSI_PERIOD = 14

MACD_FAST = 12

MACD_SLOW = 26

MACD_SIGNAL = 9

ADX_PERIOD = 14

ATR_PERIOD = 14

VOLUME_MA_PERIOD = 20


# ============================================================
# FILTERS
# ============================================================

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_VOLUME_FILTER = True


# ============================================================
# SL / TP
# ============================================================

AUTO_SLTP = True

ATR_SL_MULTIPLIER = 1.5

ATR_TP_MULTIPLIER = 3.0


# ============================================================
# POSITION MANAGEMENT
# ============================================================

BREAK_EVEN_ENABLED = True

BREAK_EVEN_TRIGGER_PERCENT = 1.0

BREAK_EVEN_OFFSET_PERCENT = 0.05

TRAILING_ENABLED = True

TRAILING_START_PERCENT = 1.5

TRAILING_DISTANCE_PERCENT = 0.75


# ============================================================
# MT5
# ============================================================

MT5_TERMINAL_PATH = _env_str(
    "MT5_TERMINAL_PATH",
    r"C:\MT5-Pourya\terminal64.exe",
)

MT5_PORTABLE = True

MT5_TIMEOUT = 60000

MT5_DEVIATION = 20

MT5_MAGIC_NUMBER = 20260731

MT5_ORDER_COMMENT = "Pourya Trader AI"


# ============================================================
# LOOP
# ============================================================

TRADING_INTERVAL = 60

SCHEDULER_INTERVAL = 60

SCHEDULER_MODE = "RUNNING"


# ============================================================
# RETRIES
# ============================================================

MAX_RETRIES = 3

# IMPORTANT:
# This value must NOT be used to retry mt5.order_send().
# Order submission is single-shot to prevent duplicate trades.


# ============================================================
# DATABASE
# ============================================================

DATABASE_PATH = str(
    BASE_DIR / "data" / "pourya_trader.db"
)


# ============================================================
# SAFETY ASSERTIONS
# ============================================================

assert PILOT_SYMBOL == "XAUUSD.su"

assert MIN_PROJECT_LOT == 0.01

assert MAX_PROJECT_LOT == 0.03

assert MAX_OPEN_TRADES == 5

assert NO_MARTINGALE is True

assert MAX_DAILY_LOSS_PERCENT == 5.0

assert MIN_RISK_REWARD >= 2.0

# Live trading must remain explicitly locked.
# The connector performs the final runtime check.
