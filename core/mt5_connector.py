# core/mt5_connector.py

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import MetaTrader5 as mt5

from config import (
    ALLOW_LIVE_TRADING,
    DEFAULT_LOT,
    MAX_OPEN_TRADES,
    MT5_DEVIATION,
    MT5_MAGIC_NUMBER,
    MT5_ORDER_COMMENT,
    PAPER_TRADING,
    SYMBOLS,
)

from core.logger import logger


# ============================================================
# PROJECT SAFETY CONSTANTS
# ============================================================

PILOT_SYMBOL = "XAUUSD.su"

DEFAULT_SYMBOL = PILOT_SYMBOL
DEFAULT_MAGIC = int(MT5_MAGIC_NUMBER)
DEFAULT_DEVIATION = int(MT5_DEVIATION)
DEFAULT_COMMENT = str(MT5_ORDER_COMMENT)

MIN_PROJECT_LOT = 0.01
MAX_PROJECT_LOT = 0.03
MAX_PROJECT_POSITIONS = 5

PROJECT_MAX_POSITIONS = min(
    MAX_PROJECT_POSITIONS,
    int(MAX_OPEN_TRADES),
)

MT5_PATH = r"C:\MT5-Pourya\terminal64.exe"

DEFAULT_TIMEFRAME = "15"


# ============================================================
# TIMEFRAME MAP
# ============================================================

TIMEFRAME_MAP = {
    "1": mt5.TIMEFRAME_M1,
    "5": mt5.TIMEFRAME_M5,
    "15": mt5.TIMEFRAME_M15,
    "30": mt5.TIMEFRAME_M30,
    "60": mt5.TIMEFRAME_H1,
    "240": mt5.TIMEFRAME_H4,
    "1440": mt5.TIMEFRAME_D1,
}


# ============================================================
# CONNECTION STATE
# ============================================================

_initialized_by_project = False


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _safe_float(value: Any) -> Optional[float]:
    try:
        result = float(value)

        if not math.isfinite(result):
            return None

        return result

    except Exception:
        return None


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


def _normalize_symbol(symbol: Any) -> str:
    if symbol is None:
        return ""

    return str(symbol).strip()


def _is_pilot_symbol(symbol: Any) -> bool:
    return (
        _normalize_symbol(symbol).upper()
        == PILOT_SYMBOL.upper()
    )


def _is_project_position(
    position: Any,
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
) -> bool:

    if position is None:
        return False

    position_symbol = getattr(
        position,
        "symbol",
        None,
    )

    position_magic = getattr(
        position,
        "magic",
        None,
    )

    if (
        _normalize_symbol(position_symbol).upper()
        != _normalize_symbol(symbol).upper()
    ):
        return False

    try:
        if int(position_magic) != int(magic):
            return False
    except Exception:
        return False

    return True


# ============================================================
# LIVE TRADING GATE
# ============================================================

def live_trading_allowed() -> bool:
    """
    Independent fail-closed live-trading gate.

    Live trading requires:
        ALLOW_LIVE_TRADING=True
        PAPER_TRADING=False

    Anything else blocks real order execution.
    """

    try:
        return (
            bool(ALLOW_LIVE_TRADING)
            and not bool(PAPER_TRADING)
        )

    except Exception as exc:
        logger.exception(
            "MT5 LIVE GATE ERROR: %s",
            exc,
        )

        return False


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_mt5() -> bool:
    """
    Initialize the dedicated portable MT5 terminal.

    The function:
        1. shuts down any existing Python MT5 connection,
        2. initializes the portable terminal,
        3. verifies terminal connectivity,
        4. verifies account information.
    """

    global _initialized_by_project

    try:
        logger.info("=" * 70)
        logger.info("MT5 CONNECTOR: INITIALIZATION")
        logger.info("=" * 70)

        try:
            mt5.shutdown()
        except Exception:
            pass

        initialized = mt5.initialize(
            path=MT5_PATH,
            portable=True,
            timeout=60000,
        )

        if not initialized:

            error = mt5.last_error()

            logger.error(
                "MT5 INITIALIZE FAILED | error=%s",
                error,
            )

            _initialized_by_project = False

            return False

        terminal = mt5.terminal_info()

        if terminal is None:

            logger.error(
                "MT5 TERMINAL INFO FAILED | error=%s",
                mt5.last_error(),
            )

            try:
                mt5.shutdown()
            except Exception:
                pass

            _initialized_by_project = False

            return False

        if not bool(
            getattr(
                terminal,
                "connected",
                False,
            )
        ):

            logger.error(
                "MT5 TERMINAL NOT CONNECTED"
            )

            try:
                mt5.shutdown()
            except Exception:
                pass

            _initialized_by_project = False

            return False

        account = mt5.account_info()

        if account is None:

            logger.error(
                "MT5 ACCOUNT INFO FAILED | error=%s",
                mt5.last_error(),
            )

            try:
                mt5.shutdown()
            except Exception:
                pass

            _initialized_by_project = False

            return False

        _initialized_by_project = True

        logger.info(
            "MT5 INITIALIZATION SUCCESS"
        )

        logger.info(
            "MT5 ACCOUNT | login=%s | server=%s | "
            "balance=%s | equity=%s | currency=%s",
            getattr(account, "login", None),
            getattr(account, "server", None),
            getattr(account, "balance", None),
            getattr(account, "equity", None),
            getattr(account, "currency", None),
        )

        logger.info(
            "MT5 TRADING PERMISSIONS | "
            "trade_allowed=%s | trade_expert=%s",
            getattr(account, "trade_allowed", None),
            getattr(account, "trade_expert", None),
        )

        logger.info(
            "MT5 PILOT SYMBOL=%s",
            PILOT_SYMBOL,
        )

        return True

    except Exception as exc:

        logger.exception(
            "MT5 INITIALIZATION ERROR: %s",
            exc,
        )

        _initialized_by_project = False

        try:
            mt5.shutdown()
        except Exception:
            pass

        return False


def shutdown_mt5() -> bool:
    """
    Shutdown the Python MT5 connection.
    """

    global _initialized_by_project

    try:

        mt5.shutdown()

        _initialized_by_project = False

        logger.info(
            "MT5 CONNECTOR: SHUTDOWN COMPLETE"
        )

        return True

    except Exception as exc:

        logger.exception(
            "MT5 SHUTDOWN ERROR: %s",
            exc,
        )

        _initialized_by_project = False

        return False


# ============================================================
# CONNECTION CHECK
# ============================================================

def is_connected() -> bool:
    """
    Verify MT5 terminal and account connectivity.
    """

    try:

        terminal = mt5.terminal_info()

        if terminal is None:
            return False

        if not bool(
            getattr(
                terminal,
                "connected",
                False,
            )
        ):
            return False

        account = mt5.account_info()

        if account is None:
            return False

        return True

    except Exception:

        return False


def ensure_connection() -> bool:
    """
    Ensure an active MT5 connection.

    If connection is unavailable, attempt one controlled
    initialization. No order retry is performed here.
    """

    if is_connected():
        return True

    logger.warning(
        "MT5 CONNECTION LOST - REINITIALIZING"
    )

    return initialize_mt5()


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info() -> Optional[Any]:
    try:

        if not ensure_connection():
            return None

        return mt5.account_info()

    except Exception as exc:

        logger.exception(
            "MT5 ACCOUNT INFO ERROR: %s",
            exc,
        )

        return None


def get_account_snapshot() -> Optional[Dict[str, Any]]:
    """
    Return normalized account snapshot.
    """

    account = get_account_info()

    if account is None:
        return None

    try:

        return {
            "login": getattr(
                account,
                "login",
                None,
            ),
            "server": getattr(
                account,
                "server",
                None,
            ),
            "currency": getattr(
                account,
                "currency",
                None,
            ),
            "balance": float(
                getattr(
                    account,
                    "balance",
                    0.0,
                )
            ),
            "equity": float(
                getattr(
                    account,
                    "equity",
                    0.0,
                )
            ),
            "profit": float(
                getattr(
                    account,
                    "profit",
                    0.0,
                )
            ),
            "margin": float(
                getattr(
                    account,
                    "margin",
                    0.0,
                )
            ),
            "free_margin": float(
                getattr(
                    account,
                    "margin_free",
                    0.0,
                )
            ),
            "margin_level": getattr(
                account,
                "margin_level",
                None,
            ),
            "trade_allowed": bool(
                getattr(
                    account,
                    "trade_allowed",
                    False,
                )
            ),
            "trade_expert": bool(
                getattr(
                    account,
                    "trade_expert",
                    False,
                )
            ),
            "leverage": getattr(
                account,
                "leverage",
                None,
            ),
            "margin_mode": getattr(
                account,
                "margin_mode",
                None,
            ),
        }

    except Exception as exc:

        logger.exception(
            "MT5 ACCOUNT SNAPSHOT ERROR: %s",
            exc,
        )

        return None


def get_margin_mode() -> Optional[int]:
    """
    Return MT5 account margin mode.

    This is important because hedging accounts can hold
    multiple independent positions on the same symbol,
    while netting accounts cannot.
    """

    account = get_account_info()

    if account is None:
        return None

    try:
        return int(
            getattr(
                account,
                "margin_mode",
            )
        )

    except Exception:
        return None


def get_account_trading_permissions() -> Dict[str, bool]:
    account = get_account_info()

    if account is None:
        return {
            "account_available": False,
            "trade_allowed": False,
            "trade_expert": False,
        }

    return {
        "account_available": True,
        "trade_allowed": bool(
            getattr(
                account,
                "trade_allowed",
                False,
            )
        ),
        "trade_expert": bool(
            getattr(
                account,
                "trade_expert",
                False,
            )
        ),
    }


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol: str = DEFAULT_SYMBOL,
) -> Optional[Any]:

    symbol = _normalize_symbol(symbol)

    if not _is_pilot_symbol(symbol):

        logger.error(
            "SYMBOL BLOCKED | requested=%s | pilot=%s",
            symbol,
            PILOT_SYMBOL,
        )

        return None

    try:

        if not ensure_connection():
            return None

        info = mt5.symbol_info(symbol)

        if info is None:

            logger.error(
                "SYMBOL INFO FAILED | symbol=%s | error=%s",
                symbol,
                mt5.last_error(),
            )

            return None

        if not bool(
            getattr(
                info,
                "visible",
                True,
            )
        ):

            selected = mt5.symbol_select(
                symbol,
                True,
            )

            if not selected:

                logger.error(
                    "SYMBOL SELECT FAILED | symbol=%s",
                    symbol,
                )

                return None

            info = mt5.symbol_info(symbol)

        return info

    except Exception as exc:

        logger.exception(
            "SYMBOL INFO ERROR: %s",
            exc,
        )

        return None


def get_symbol_tick(
    symbol: str = DEFAULT_SYMBOL,
) -> Optional[Any]:

    symbol = _normalize_symbol(symbol)

    if not _is_pilot_symbol(symbol):
        return None

    try:

        if not ensure_connection():
            return None

        tick = mt5.symbol_info_tick(
            symbol
        )

        if tick is None:

            logger.error(
                "SYMBOL TICK FAILED | symbol=%s | error=%s",
                symbol,
                mt5.last_error(),
            )

            return None

        return tick

    except Exception as exc:

        logger.exception(
            "SYMBOL TICK ERROR: %s",
            exc,
        )

        return None


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(
    symbol: str = DEFAULT_SYMBOL,
) -> int:

    info = get_symbol_info(symbol)

    if info is None:
        return mt5.ORDER_FILLING_IOC

    try:

        filling_mode = int(
            getattr(
                info,
                "filling_mode",
                0,
            )
        )

        # MT5 SYMBOL_FILLING_FOK = 1
        if filling_mode & 1:
            return mt5.ORDER_FILLING_FOK

        # MT5 SYMBOL_FILLING_IOC = 2
        if filling_mode & 2:
            return mt5.ORDER_FILLING_IOC

        return mt5.ORDER_FILLING_RETURN

    except Exception:

        return mt5.ORDER_FILLING_IOC


# ============================================================
# TIMEFRAME
# ============================================================

def get_timeframe(
    timeframe: Any,
) -> Optional[int]:

    key = str(timeframe).strip()

    return TIMEFRAME_MAP.get(key)


# ============================================================
# MARKET DATA
# ============================================================

def get_rates(
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
    count: int = 200,
) -> Optional[List[Any]]:

    symbol = _normalize_symbol(symbol)

    if not _is_pilot_symbol(symbol):

        logger.error(
            "RATES BLOCKED | symbol=%s",
            symbol,
        )

        return None

    try:

        if not ensure_connection():
            return None

        tf = get_timeframe(
            timeframe
        )

        if tf is None:

            logger.error(
                "INVALID TIMEFRAME | %s",
                timeframe,
            )

            return None

        count = int(count)

        if count <= 0:
            return None

        rates = mt5.copy_rates_from_pos(
            symbol,
            tf,
            0,
            count,
        )

        if rates is None:

            logger.error(
                "COPY RATES FAILED | symbol=%s | "
                "timeframe=%s | error=%s",
                symbol,
                timeframe,
                mt5.last_error(),
            )

            return None

        if len(rates) == 0:
            return None

        return rates

    except Exception as exc:

        logger.exception(
            "GET RATES ERROR: %s",
            exc,
        )

        return None


# ============================================================
# PRICE NORMALIZATION
# ============================================================

def normalize_price(
    symbol: str,
    price: Any,
) -> Optional[float]:

    symbol = _normalize_symbol(symbol)

    if not _is_pilot_symbol(symbol):
        return None

    value = _safe_float(price)

    if value is None or value <= 0:
        return None

    info = get_symbol_info(symbol)

    if info is None:
        return None

    try:

        digits = int(
            getattr(
                info,
                "digits",
                2,
            )
        )

        return round(
            value,
            digits,
        )

    except Exception:
        return None


# ============================================================
# VOLUME NORMALIZATION
# ============================================================

def normalize_volume(
    symbol: str,
    volume: Any,
) -> float:

    symbol = _normalize_symbol(symbol)

    if not _is_pilot_symbol(symbol):
        return 0.0

    value = _safe_float(volume)

    if value is None:
        return 0.0

    # HARD PROJECT LIMIT.
    # Never silently cap a requested lot above 0.03.
    if value > MAX_PROJECT_LOT:
        logger.error(
            "LOT BLOCKED | requested=%s | max=%s",
            value,
            MAX_PROJECT_LOT,
        )

        return 0.0

    if value < MIN_PROJECT_LOT:
        logger.error(
            "LOT BLOCKED | requested=%s | min=%s",
            value,
            MIN_PROJECT_LOT,
        )

        return 0.0

    info = get_symbol_info(symbol)

    if info is None:
        return 0.0

    try:

        volume_min = max(
            MIN_PROJECT_LOT,
            float(
                getattr(
                    info,
                    "volume_min",
                    MIN_PROJECT_LOT,
                )
            ),
        )

        volume_max = min(
            MAX_PROJECT_LOT,
            float(
                getattr(
                    info,
                    "volume_max",
                    MAX_PROJECT_LOT,
                )
            ),
        )

        volume_step = float(
            getattr(
                info,
                "volume_step",
                0.01,
            )
        )

        if volume_step <= 0:
            volume_step = 0.01

        if value < volume_min:
            return 0.0

        if value > volume_max:
            return 0.0

        steps = math.floor(
            (
                value - volume_min
            ) / volume_step
            + 1e-9
        )

        normalized = (
            volume_min
            + steps * volume_step
        )

        normalized = round(
            normalized,
            8,
        )

        if normalized < MIN_PROJECT_LOT:
            return 0.0

        if normalized > MAX_PROJECT_LOT:
            return 0.0

        return normalized

    except Exception as exc:

        logger.exception(
            "VOLUME NORMALIZATION ERROR: %s",
            exc,
        )

        return 0.0


# ============================================================
# STOP / FREEZE DISTANCE
# ============================================================

def get_stop_freeze_distance(
    symbol: str = DEFAULT_SYMBOL,
) -> float:

    info = get_symbol_info(symbol)

    if info is None:
        return 0.0

    try:

        point = float(
            getattr(
                info,
                "point",
                0.0,
            )
        )

        stops_level = int(
            getattr(
                info,
                "trade_stops_level",
                0,
            )
        )

        freeze_level = int(
            getattr(
                info,
                "trade_freeze_level",
                0,
            )
        )

        level = max(
            stops_level,
            freeze_level,
        )

        return max(
            0.0,
            point * level,
        )

    except Exception:
        return 0.0


# ============================================================
# SL / TP VALIDATION
# ============================================================

def validate_sl_tp(
    symbol: str,
    side: str,
    entry: float,
    sl: float,
    tp: float,
) -> Tuple[bool, str]:

    symbol = _normalize_symbol(symbol)
    side = str(side).strip().upper()

    if not _is_pilot_symbol(symbol):
        return False, "PILOT_SYMBOL_ONLY"

    entry_value = _safe_float(entry)
    sl_value = _safe_float(sl)
    tp_value = _safe_float(tp)

    if (
        entry_value is None
        or sl_value is None
        or tp_value is None
    ):
        return False, "INVALID_PRICE"

    if (
        entry_value <= 0
        or sl_value <= 0
        or tp_value <= 0
    ):
        return False, "NON_POSITIVE_PRICE"

    minimum_distance = get_stop_freeze_distance(
        symbol
    )

    if side == "BUY":

        if sl_value >= entry_value:
            return False, "BUY_SL_NOT_BELOW_ENTRY"

        if tp_value <= entry_value:
            return False, "BUY_TP_NOT_ABOVE_ENTRY"

        if minimum_distance > 0:

            if (
                entry_value - sl_value
                < minimum_distance
            ):
                return False, "BUY_SL_TOO_CLOSE"

            if (
                tp_value - entry_value
                < minimum_distance
            ):
                return False, "BUY_TP_TOO_CLOSE"

    elif side == "SELL":

        if sl_value <= entry_value:
            return False, "SELL_SL_NOT_ABOVE_ENTRY"

        if tp_value >= entry_value:
            return False, "SELL_TP_NOT_BELOW_ENTRY"

        if minimum_distance > 0:

            if (
                sl_value - entry_value
                < minimum_distance
            ):
                return False, "SELL_SL_TOO_CLOSE"

            if (
                entry_value - tp_value
                < minimum_distance
            ):
                return False, "SELL_TP_TOO_CLOSE"

    else:

        return False, "INVALID_SIDE"

    return True, "OK"


# ============================================================
# POSITIONS
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None,
) -> List[Any]:

    try:

        if not ensure_connection():
            return []

        if symbol is not None:

            symbol = _normalize_symbol(symbol)

            if not _is_pilot_symbol(symbol):
                return []

            positions = mt5.positions_get(
                symbol=symbol
            )

        else:

            positions = mt5.positions_get()

        if positions is None:
            return []

        return list(positions)

    except Exception as exc:

        logger.exception(
            "GET OPEN POSITIONS ERROR: %s",
            exc,
        )

        return []


def get_project_positions(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
) -> List[Any]:

    if not _is_pilot_symbol(symbol):
        return []

    positions = get_open_positions(
        symbol
    )

    return [
        position
        for position in positions
        if _is_project_position(
            position,
            symbol=symbol,
            magic=magic,
        )
    ]


def get_open_position_count(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
) -> int:

    return len(
        get_project_positions(
            symbol=symbol,
            magic=magic,
        )
    )


def validate_position_limit(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
) -> Tuple[bool, str]:

    count = get_open_position_count(
        symbol=symbol,
        magic=magic,
    )

    if count >= PROJECT_MAX_POSITIONS:

        return (
            False,
            (
                f"PROJECT_POSITION_LIMIT_REACHED:"
                f"{count}/{PROJECT_MAX_POSITIONS}"
            ),
        )

    return True, "OK"


# ============================================================
# MARGIN
# ============================================================

def calculate_margin(
    symbol: str,
    side: str,
    volume: float,
    price: float,
) -> Optional[float]:

    symbol = _normalize_symbol(symbol)
    side = str(side).strip().upper()

    if not _is_pilot_symbol(symbol):
        return None

    if side == "BUY":
        order_type = mt5.ORDER_TYPE_BUY

    elif side == "SELL":
        order_type = mt5.ORDER_TYPE_SELL

    else:
        return None

    try:

        if not ensure_connection():
            return None

        result = mt5.order_calc_margin(
            order_type,
            symbol,
            float(volume),
            float(price),
        )

        if result is None:
            return None

        return float(result)

    except Exception as exc:

        logger.exception(
            "MARGIN CALCULATION ERROR: %s",
            exc,
        )

        return None


def validate_free_margin(
    symbol: str,
    side: str,
    volume: float,
    price: float,
) -> Tuple[bool, str]:

    account = get_account_info()

    if account is None:
        return False, "ACCOUNT_UNAVAILABLE"

    margin = calculate_margin(
        symbol,
        side,
        volume,
        price,
    )

    if margin is None:
        return False, "MARGIN_CALC_FAILED"

    free_margin = float(
        getattr(
            account,
            "margin_free",
            0.0,
        )
    )

    if margin > free_margin:
        return (
            False,
            (
                f"INSUFFICIENT_MARGIN:"
                f"required={margin}:"
                f"free={free_margin}"
            ),
        )

    return True, "OK"


# ============================================================
# ORDER TYPE
# ============================================================

def _get_order_type(
    side: str,
) -> Optional[int]:

    side = str(side).strip().upper()

    if side == "BUY":
        return mt5.ORDER_TYPE_BUY

    if side == "SELL":
        return mt5.ORDER_TYPE_SELL

    return None


# ============================================================
# MARKET ORDER REQUEST
# ============================================================

def _build_market_request(
    symbol: str,
    side: str,
    volume: float,
    sl: float,
    tp: float,
    magic: int = DEFAULT_MAGIC,
    comment: str = DEFAULT_COMMENT,
) -> Optional[Dict[str, Any]]:

    symbol = _normalize_symbol(symbol)
    side = str(side).strip().upper()

    if not _is_pilot_symbol(symbol):
        return None

    order_type = _get_order_type(side)

    if order_type is None:
        return None

    tick = get_symbol_tick(symbol)

    if tick is None:
        return None

    if side == "BUY":

        price = _safe_float(
            getattr(
                tick,
                "ask",
                None,
            )
        )

    else:

        price = _safe_float(
            getattr(
                tick,
                "bid",
                None,
            )
        )

    if price is None or price <= 0:
        return None

    normalized_volume = normalize_volume(
        symbol,
        volume,
    )

    if normalized_volume <= 0:
        return None

    normalized_sl = normalize_price(
        symbol,
        sl,
    )

    normalized_tp = normalize_price(
        symbol,
        tp,
    )

    if (
        normalized_sl is None
        or normalized_tp is None
    ):
        return None

    valid, reason = validate_sl_tp(
        symbol=symbol,
        side=side,
        entry=price,
        sl=normalized_sl,
        tp=normalized_tp,
    )

    if not valid:

        logger.error(
            "ORDER REQUEST BLOCKED | SL/TP | reason=%s",
            reason,
        )

        return None

    return {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": normalized_volume,
        "type": order_type,
        "price": price,
        "sl": normalized_sl,
        "tp": normalized_tp,
        "deviation": DEFAULT_DEVIATION,
        "magic": int(magic),
        "comment": str(comment),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": get_filling_mode(symbol),
    }


# ============================================================
# ORDER CHECK
# ============================================================

def _order_check_success(
    result: Any,
) -> bool:

    if result is None:
        return False

    retcode = getattr(
        result,
        "retcode",
        None,
    )

    try:
        retcode = int(retcode)
    except Exception:
        return False

    # MT5 successful order_check normally returns
    # TRADE_RETCODE_DONE (10009).
    return retcode == mt5.TRADE_RETCODE_DONE


# ============================================================
# FINAL MARKET ORDER SAFETY GATE
# ============================================================

def check_market_order(
    symbol: str,
    side: str,
    volume: float,
    sl: float,
    tp: float,
    magic: int = DEFAULT_MAGIC,
    comment: str = DEFAULT_COMMENT,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:

    symbol = _normalize_symbol(symbol)
    side = str(side).strip().upper()

    # --------------------------------------------------------
    # CONNECTION
    # --------------------------------------------------------

    if not ensure_connection():
        return (
            False,
            None,
            "MT5_NOT_CONNECTED",
        )

    # --------------------------------------------------------
    # LIVE SAFETY GATE
    # --------------------------------------------------------

    if not live_trading_allowed():

        return (
            False,
            None,
            (
                "LIVE_TRADING_BLOCKED:"
                "PAPER_TRADING_OR_ALLOW_LIVE_TRADING"
            ),
        )

    # --------------------------------------------------------
    # PILOT SYMBOL
    # --------------------------------------------------------

    if not _is_pilot_symbol(symbol):

        return (
            False,
            None,
            "PILOT_SYMBOL_ONLY",
        )

    # --------------------------------------------------------
    # ACCOUNT PERMISSIONS
    # --------------------------------------------------------

    permissions = (
        get_account_trading_permissions()
    )

    if not permissions.get(
        "account_available",
        False,
    ):

        return (
            False,
            None,
            "ACCOUNT_UNAVAILABLE",
        )

    if not permissions.get(
        "trade_allowed",
        False,
    ):

        return (
            False,
            None,
            "ACCOUNT_TRADE_NOT_ALLOWED",
        )

    if not permissions.get(
        "trade_expert",
        False,
    ):

        return (
            False,
            None,
            "EXPERT_TRADING_NOT_ALLOWED",
        )

    # --------------------------------------------------------
    # POSITION LIMIT
    # --------------------------------------------------------

    limit_ok, limit_reason = (
        validate_position_limit(
            symbol=symbol,
            magic=magic,
        )
    )

    if not limit_ok:

        return (
            False,
            None,
            limit_reason,
        )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    requested_volume = _safe_float(
        volume
    )

    if requested_volume is None:

        return (
            False,
            None,
            "INVALID_VOLUME",
        )

    if (
        requested_volume < MIN_PROJECT_LOT
    ):

        return (
            False,
            None,
            "VOLUME_BELOW_PROJECT_MIN",
        )

    if (
        requested_volume > MAX_PROJECT_LOT
    ):

        return (
            False,
            None,
            "VOLUME_ABOVE_PROJECT_MAX",
        )

    normalized_volume = normalize_volume(
        symbol,
        requested_volume,
    )

    if normalized_volume <= 0:

        return (
            False,
            None,
            "VOLUME_NORMALIZATION_FAILED",
        )

    # --------------------------------------------------------
    # TICK / ENTRY
    # --------------------------------------------------------

    tick = get_symbol_tick(symbol)

    if tick is None:

        return (
            False,
            None,
            "TICK_UNAVAILABLE",
        )

    if side == "BUY":

        entry = _safe_float(
            getattr(
                tick,
                "ask",
                None,
            )
        )

    elif side == "SELL":

        entry = _safe_float(
            getattr(
                tick,
                "bid",
                None,
            )
        )

    else:

        return (
            False,
            None,
            "INVALID_SIDE",
        )

    if entry is None or entry <= 0:

        return (
            False,
            None,
            "INVALID_ENTRY_PRICE",
        )

    # --------------------------------------------------------
    # SL / TP
    # --------------------------------------------------------

    normalized_sl = normalize_price(
        symbol,
        sl,
    )

    normalized_tp = normalize_price(
        symbol,
        tp,
    )

    if (
        normalized_sl is None
        or normalized_tp is None
    ):

        return (
            False,
            None,
            "INVALID_SL_TP",
        )

    sl_tp_ok, sl_tp_reason = (
        validate_sl_tp(
            symbol=symbol,
            side=side,
            entry=entry,
            sl=normalized_sl,
            tp=normalized_tp,
        )
    )

    if not sl_tp_ok:

        return (
            False,
            None,
            sl_tp_reason,
        )

    # --------------------------------------------------------
    # MARGIN
    # --------------------------------------------------------

    margin_ok, margin_reason = (
        validate_free_margin(
            symbol=symbol,
            side=side,
            volume=normalized_volume,
            price=entry,
        )
    )

    if not margin_ok:

        return (
            False,
            None,
            margin_reason,
        )

    # --------------------------------------------------------
    # BUILD REQUEST
    # --------------------------------------------------------

    request = _build_market_request(
        symbol=symbol,
        side=side,
        volume=normalized_volume,
        sl=normalized_sl,
        tp=normalized_tp,
        magic=magic,
        comment=comment,
    )

    if request is None:

        return (
            False,
            None,
            "REQUEST_BUILD_FAILED",
        )

    # --------------------------------------------------------
    # FINAL MT5 ORDER CHECK
    # --------------------------------------------------------

    check_result = mt5.order_check(
        request
    )

    if check_result is None:

        return (
            False,
            None,
            (
                "ORDER_CHECK_RETURNED_NONE:"
                f"{mt5.last_error()}"
            ),
        )

    check_retcode = getattr(
        check_result,
        "retcode",
        None,
    )

    if not _order_check_success(
        check_result
    ):

        return (
            False,
            None,
            (
                "ORDER_CHECK_FAILED:"
                f"retcode={check_retcode}:"
                f"comment={getattr(check_result, 'comment', '')}"
            ),
        )

    logger.info(
        "FINAL ORDER CHECK PASSED | "
        "symbol=%s | side=%s | volume=%s | "
        "entry=%s | sl=%s | tp=%s",
        symbol,
        side,
        normalized_volume,
        entry,
        normalized_sl,
        normalized_tp,
    )

    return (
        True,
        request,
        "OK",
    )


# ============================================================
# MARKET ORDER SEND
# ============================================================

def send_market_order(
    symbol: str,
    side: str,
    volume: float,
    sl: float,
    tp: float,
    magic: int = DEFAULT_MAGIC,
    comment: str = DEFAULT_COMMENT,
) -> Dict[str, Any]:

    """
    Send exactly ONE market order.

    Important:
        There is intentionally NO automatic retry after
        mt5.order_send().

    An ambiguous result must never be retried automatically,
    because the first request may have reached the broker.
    """

    gate_ok, request, reason = (
        check_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            comment=comment,
        )
    )

    if not gate_ok:

        logger.warning(
            "MARKET ORDER BLOCKED | reason=%s",
            reason,
        )

        return {
            "success": False,
            "status": "BLOCKED",
            "reason": reason,
            "ticket": None,
            "order": None,
            "deal": None,
            "retcode": None,
        }

    try:

        logger.warning(
            "MT5 ORDER SEND | "
            "symbol=%s | side=%s | volume=%s",
            symbol,
            side,
            request.get("volume"),
        )

        result = mt5.order_send(
            request
        )

    except Exception as exc:

        logger.exception(
            "MT5 ORDER SEND EXCEPTION: %s",
            exc,
        )

        return {
            "success": False,
            "status": "AMBIGUOUS",
            "reason": str(exc),
            "ticket": None,
            "order": None,
            "deal": None,
            "retcode": None,
        }

    # --------------------------------------------------------
    # Ambiguous result
    # --------------------------------------------------------

    if result is None:

        logger.error(
            "MT5 ORDER SEND RETURNED NONE | "
            "NO AUTOMATIC RETRY | error=%s",
            mt5.last_error(),
        )

        return {
            "success": False,
            "status": "AMBIGUOUS",
            "reason": (
                "ORDER_SEND_RETURNED_NONE"
            ),
            "ticket": None,
            "order": None,
            "deal": None,
            "retcode": None,
        }

    retcode = getattr(
        result,
        "retcode",
        None,
    )

    order_ticket = getattr(
        result,
        "order",
        None,
    )

    deal_ticket = getattr(
        result,
        "deal",
        None,
    )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    success_codes = {
        mt5.TRADE_RETCODE_DONE,
        mt5.TRADE_RETCODE_DONE_PARTIAL,
    }

    if retcode in success_codes:

        ticket = (
            deal_ticket
            or order_ticket
        )

        logger.info(
            "MT5 ORDER SUCCESS | "
            "retcode=%s | order=%s | deal=%s",
            retcode,
            order_ticket,
            deal_ticket,
        )

        return {
            "success": True,
            "status": "EXECUTED",
            "reason": getattr(
                result,
                "comment",
                "",
            ),
            "ticket": ticket,
            "order": order_ticket,
            "deal": deal_ticket,
            "retcode": retcode,
            "result": result,
        }

    # --------------------------------------------------------
    # Failed order
    # --------------------------------------------------------

    logger.error(
        "MT5 ORDER FAILED | "
        "retcode=%s | comment=%s",
        retcode,
        getattr(
            result,
            "comment",
            "",
        ),
    )

    return {
        "success": False,
        "status": "REJECTED",
        "reason": getattr(
            result,
            "comment",
            "ORDER_REJECTED",
        ),
        "ticket": None,
        "order": order_ticket,
        "deal": deal_ticket,
        "retcode": retcode,
        "result": result,
    }


# ============================================================
# COMPATIBILITY TRADE STATUS
# ============================================================

def update_trade_status(
    ticket: int,
    status: str,
) -> bool:
    """
    Compatibility helper.

    Database persistence remains handled by trade_manager.
    This function intentionally does not mutate MT5 state.
    """

    logger.info(
        "TRADE STATUS | ticket=%s | status=%s",
        ticket,
        status,
    )

    return True


# ============================================================
# CONNECTOR CLASS
# ============================================================

class MT5Connector:
    """
    Object-oriented compatibility wrapper around the
    module-level MT5 connector functions.
    """

    def __init__(
        self,
        path: str = MT5_PATH,
        portable: bool = True,
    ) -> None:

        self.path = path
        self.portable = portable

    def initialize(self) -> bool:
        return initialize_mt5()

    def shutdown(self) -> bool:
        return shutdown_mt5()

    def is_connected(self) -> bool:
        return is_connected()

    def ensure_connection(self) -> bool:
        return ensure_connection()

    def get_account_info(self) -> Optional[Any]:
        return get_account_info()

    def get_account_snapshot(
        self,
    ) -> Optional[Dict[str, Any]]:
        return get_account_snapshot()

    def get_symbol_info(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> Optional[Any]:
        return get_symbol_info(symbol)

    def get_symbol_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> Optional[Any]:
        return get_symbol_tick(symbol)

    def get_rates(
        self,
        symbol: str = DEFAULT_SYMBOL,
        timeframe: str = DEFAULT_TIMEFRAME,
        count: int = 200,
    ) -> Optional[List[Any]]:
        return get_rates(
            symbol,
            timeframe,
            count,
        )

    def get_open_positions(
        self,
        symbol: Optional[str] = None,
    ) -> List[Any]:
        return get_open_positions(symbol)

    def get_project_positions(
        self,
        symbol: str = PILOT_SYMBOL,
        magic: int = DEFAULT_MAGIC,
    ) -> List[Any]:
        return get_project_positions(
            symbol,
            magic,
        )

    def get_open_position_count(
        self,
        symbol: str = PILOT_SYMBOL,
        magic: int = DEFAULT_MAGIC,
    ) -> int:
        return get_open_position_count(
            symbol,
            magic,
        )

    def normalize_volume(
        self,
        symbol: str,
        volume: Any,
    ) -> float:
        return normalize_volume(
            symbol,
            volume,
        )

    def normalize_price(
        self,
        symbol: str,
        price: Any,
    ) -> Optional[float]:
        return normalize_price(
            symbol,
            price,
        )

    def send_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        sl: float,
        tp: float,
        magic: int = DEFAULT_MAGIC,
        comment: str = DEFAULT_COMMENT,
    ) -> Dict[str, Any]:
        return send_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            comment=comment,
        )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "PILOT_SYMBOL",
    "DEFAULT_SYMBOL",
    "DEFAULT_MAGIC",
    "DEFAULT_DEVIATION",
    "DEFAULT_COMMENT",
    "MIN_PROJECT_LOT",
    "MAX_PROJECT_LOT",
    "MAX_PROJECT_POSITIONS",
    "PROJECT_MAX_POSITIONS",
    "MT5_PATH",
    "TIMEFRAME_MAP",
    "live_trading_allowed",
    "initialize_mt5",
    "shutdown_mt5",
    "is_connected",
    "ensure_connection",
    "get_account_info",
    "get_account_snapshot",
    "get_margin_mode",
    "get_account_trading_permissions",
    "get_symbol_info",
    "get_symbol_tick",
    "get_filling_mode",
    "get_timeframe",
    "get_rates",
    "normalize_price",
    "normalize_volume",
    "get_stop_freeze_distance",
    "validate_sl_tp",
    "get_open_positions",
    "get_project_positions",
    "get_open_position_count",
    "validate_position_limit",
    "calculate_margin",
    "validate_free_margin",
    "check_market_order",
    "send_market_order",
    "update_trade_status",
    "MT5Connector",
]
