from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# PROJECT ROOT / ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


# ============================================================
# BASIC PROJECT INFO
# ============================================================

BOT_NAME = "Pourya Trader AI"

BOT_VERSION = "2.1.0-MT5"


# ============================================================
# ENV HELPERS
# ============================================================

def _env_str(
    name: str,
    default: str = "",
) -> str:

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip()


def _env_int(
    name: str,
    default: int = 0,
) -> int:

    try:

        return int(
            os.getenv(
                name,
                str(default),
            ).strip()
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def _env_float(
    name: str,
    default: float = 0.0,
) -> float:

    try:

        return float(
            os.getenv(
                name,
                str(default),
            ).strip()
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def _env_bool(
    name: str,
    default: bool = False,
) -> bool:

    value = os.getenv(name)

    if value is None:
        return default

    return (
        value.strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )


# ============================================================
# MT5 CONNECTION
# ============================================================

MT5_LOGIN = _env_int(
    "MT5_LOGIN",
    0,
)

MT5_PASSWORD = _env_str(
    "MT5_PASSWORD",
    "",
)

MT5_SERVER = _env_str(
    "MT5_SERVER",
    "OtetGroup-MT5",
)

MT5_TERMINAL_PATH = _env_str(
    "MT5_TERMINAL_PATH",
    r"C:\MT5-Pourya\terminal64.exe",
)

MT5_PORTABLE = _env_bool(
    "MT5_PORTABLE",
    True,
)

MT5_TIMEOUT = _env_int(
    "MT5_TIMEOUT",
    60000,
)


# ============================================================
# BROKER / MARKET
# ============================================================

BROKER = "MT5"

MARKET_TYPE = "FOREX"


# ============================================================
# TELEGRAM
# ============================================================

BOT_TOKEN = _env_str(
    "BOT_TOKEN",
    "",
)

CHAT_ID = _env_str(
    "CHAT_ID",
    "",
)


# ============================================================
# TRADING MODE
# ============================================================

AUTO_TRADE = True

# IMPORTANT:
# Keep these values closed until final explicit approval.
PAPER_TRADING = True

ALLOW_LIVE_TRADING = False

AUTO_CLOSE = True


# ============================================================
# ORDER SETTINGS
# ============================================================

ORDER_TYPE = "market"

POSITION_SIDE = "both"

MARGIN_MODE = "broker"

LEVERAGE = 100


# ============================================================
# PILOT SYMBOL
# ============================================================

PILOT_SYMBOL = "XAUUSD.su"

SYMBOLS = [
    PILOT_SYMBOL,
]


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


# ============================================================
# MT5 ORDER PARAMETERS
# ============================================================

MT5_DEVIATION = _env_int(
    "MT5_DEVIATION",
    20,
)

MT5_MAGIC_NUMBER = _env_int(
    "MT5_MAGIC_NUMBER",
    20260731,
)

MT5_ORDER_COMMENT = _env_str(
    "MT5_ORDER_COMMENT",
    "Pourya Trader AI",
)


# ============================================================
# SL / TP
# ============================================================

DEFAULT_TP = 5.0

DEFAULT_SL = 2.0


# ============================================================
# COMPATIBILITY BALANCE
# ============================================================

# Compatibility value only.
# NEVER use this value as the live account risk baseline.
# Live risk calculations must use actual MT5 account equity/balance.
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
# LOOP / SCHEDULER
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
# SIGNAL FILTERS
# ============================================================

MIN_CONFIDENCE = 60

USE_MULTI_TIMEFRAME = True

USE_VOLUME_FILTER = True

USE_ADX_FILTER = True

USE_RSI_FILTER = True

USE_MACD_FILTER = True

USE_ATR_FILTER = True


# ============================================================
# ATR / AUTOMATIC SL-TP
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
# ENV PATH
# ============================================================

ENV_FILE_PATH = str(
    ENV_FILE
)


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

# Some legacy modules may import these names directly.

MT5_PATH = MT5_TERMINAL_PATH

MT5_PORTABLE_MODE = MT5_PORTABLE

MT5_CONNECTION_TIMEOUT = MT5_TIMEOUT


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Project
    "PROJECT_ROOT",
    "ENV_FILE",
    "ENV_FILE_PATH",
    "BOT_NAME",
    "BOT_VERSION",

    # MT5
    "MT5_LOGIN",
    "MT5_PASSWORD",
    "MT5_SERVER",
    "MT5_TERMINAL_PATH",
    "MT5_PORTABLE",
    "MT5_TIMEOUT",
    "MT5_PATH",
    "MT5_PORTABLE_MODE",
    "MT5_CONNECTION_TIMEOUT",

    # Broker / market
    "BROKER",
    "MARKET_TYPE",
    "PILOT_SYMBOL",
    "SYMBOLS",

    # Telegram
    "BOT_TOKEN",
    "CHAT_ID",

    # Trading mode
    "AUTO_TRADE",
    "PAPER_TRADING",
    "ALLOW_LIVE_TRADING",
    "AUTO_CLOSE",
    "ORDER_TYPE",
    "POSITION_SIDE",
    "MARGIN_MODE",
    "LEVERAGE",

    # Positions
    "MAX_OPEN_TRADES",
    "MAX_PROJECT_POSITIONS",

    # Lots
    "MIN_PROJECT_LOT",
    "DEFAULT_LOT",
    "MAX_PROJECT_LOT",

    # Risk
    "RISK_PER_TRADE",
    "RISK_REWARD",
    "MIN_RISK_REWARD",
    "MAX_DAILY_LOSS_PERCENT",
    "INITIAL_BALANCE",

    # MT5 order
    "MT5_DEVIATION",
    "MT5_MAGIC_NUMBER",
    "MT5_ORDER_COMMENT",

    # SL / TP
    "DEFAULT_TP",
    "DEFAULT_SL",

    # Timeframes
    "TIMEFRAME",
    "TIMEFRAMES",

    # Loop
    "TRADING_INTERVAL",
    "SCHEDULER_INTERVAL",
    "SCHEDULER_MODE",

    # Request
    "REQUEST_TIMEOUT",
    "MAX_RETRIES",

    # Signals
    "MIN_CONFIDENCE",
    "USE_MULTI_TIMEFRAME",
    "USE_VOLUME_FILTER",
    "USE_ADX_FILTER",
    "USE_RSI_FILTER",
    "USE_MACD_FILTER",
    "USE_ATR_FILTER",

    # ATR
    "ENABLE_AUTO_SL_TP",
    "ATR_PERIOD",
    "ATR_SL_MULTIPLIER",
    "ATR_TP_MULTIPLIER",

    # Break-even
    "ENABLE_BREAK_EVEN",
    "BREAK_EVEN_TRIGGER_PERCENT",
    "BREAK_EVEN_OFFSET_PERCENT",

    # Trailing
    "ENABLE_TRAILING_STOP",
    "TRAILING_START_PERCENT",
    "TRAILING_DISTANCE_PERCENT",
]
