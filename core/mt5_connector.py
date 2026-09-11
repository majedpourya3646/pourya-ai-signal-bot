# core/mt5_connector.py

from __future__ import annotations

import math
import os
import platform
from typing import Any, Dict, Optional

import MetaTrader5 as mt5


# ============================================================
# PROJECT SAFETY CONFIG
# ============================================================

MT5_TIMEOUT = 60000

PILOT_SYMBOL = "XAUUSD.su"
DEFAULT_SYMBOL = PILOT_SYMBOL

DEFAULT_MAGIC = 20260731
DEFAULT_DEVIATION = 20
DEFAULT_COMMENT = "Pourya Trader AI"

MIN_PROJECT_LOT = 0.01
MAX_PROJECT_LOT = 0.03
MAX_PROJECT_POSITIONS = 5

DEFAULT_TERMINAL_PATH = r"C:\MT5-Pourya\terminal64.exe"


# ============================================================
# CONFIG IMPORT
# ============================================================

try:

    from config import (
        MT5_LOGIN,
        MT5_PASSWORD,
        MT5_SERVER,
        PAPER_TRADING,
        ALLOW_LIVE_TRADING,
        MAX_OPEN_TRADES,
    )

except Exception:

    MT5_LOGIN = int(
        os.getenv(
            "MT5_LOGIN",
            "33345335",
        )
    )

    MT5_PASSWORD = os.getenv(
        "MT5_PASSWORD",
        "",
    )

    MT5_SERVER = os.getenv(
        "MT5_SERVER",
        "ePlanet-MT5",
    )

    PAPER_TRADING = True

    ALLOW_LIVE_TRADING = False

    MAX_OPEN_TRADES = 5


# ============================================================
# PROJECT LIMIT NORMALIZATION
# ============================================================

try:

    PROJECT_MAX_POSITIONS = min(
        MAX_PROJECT_POSITIONS,
        max(
            1,
            int(MAX_OPEN_TRADES),
        ),
    )

except Exception:

    PROJECT_MAX_POSITIONS = MAX_PROJECT_POSITIONS


# ============================================================
# TERMINAL PATH
# ============================================================

def get_terminal_path() -> str:
    """
    Return the verified MT5 terminal path.
    """

    path = os.getenv(
        "MT5_TERMINAL_PATH",
        DEFAULT_TERMINAL_PATH,
    )

    return str(path).strip()


# ============================================================
# LIVE TRADING GATE
# ============================================================

def live_trading_allowed() -> bool:
    """
    Independent fail-closed live trading gate.

    Live trading is allowed only when:
        PAPER_TRADING == False
        AND
        ALLOW_LIVE_TRADING == True
    """

    try:

        return (
            not bool(PAPER_TRADING)
            and bool(ALLOW_LIVE_TRADING)
        )

    except Exception:

        return False


# ============================================================
# MT5 INITIALIZATION
# ============================================================

def initialize_mt5(
    password: Optional[str] = None,
) -> bool:
    """
    Initialize MT5 through the verified portable terminal.

    No forced Python login is performed because the verified
    environment uses the authenticated portable terminal.
    """

    if platform.system().lower() != "windows":

        return False

    terminal_path = get_terminal_path()

    try:

        try:

            mt5.shutdown()

        except Exception:

            pass

        result = mt5.initialize(
            path=terminal_path,
            portable=True,
            timeout=MT5_TIMEOUT,
        )

        if not result:

            return False

        terminal_info = mt5.terminal_info()

        if terminal_info is None:

            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        connected = bool(
            getattr(
                terminal_info,
                "connected",
                False,
            )
        )

        if not connected:

            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        account = mt5.account_info()

        if account is None:

            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        return True

    except Exception:

        try:
            mt5.shutdown()
        except Exception:
            pass

        return False


# ============================================================
# CONNECTION
# ============================================================

def is_connected() -> bool:

    try:

        info = mt5.terminal_info()

        return (
            info is not None
            and bool(
                getattr(
                    info,
                    "connected",
                    False,
                )
            )
        )

    except Exception:

        return False


def ensure_connection() -> bool:
    """
    Ensure MT5 is initialized and connected.

    Exactly one controlled initialization attempt is made
    when the current connection is unavailable.
    """

    if is_connected():

        return True

    return initialize_mt5()


def shutdown_mt5() -> None:

    try:

        mt5.shutdown()

    except Exception:

        pass


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info():

    try:

        if not ensure_connection():

            return None

        return mt5.account_info()

    except Exception:

        return None


def get_account_snapshot() -> Optional[Dict[str, Any]]:
    """
    Return live account state used by risk management.

    No hardcoded balance is used.
    """

    try:

        account = get_account_info()

        if account is None:

            return None

        return {

            "login":
                getattr(
                    account,
                    "login",
                    None,
                ),

            "server":
                getattr(
                    account,
                    "server",
                    None,
                ),

            "currency":
                getattr(
                    account,
                    "currency",
                    None,
                ),

            "balance":
                float(
                    getattr(
                        account,
                        "balance",
                        0.0,
                    )
                    or 0.0
                ),

            "equity":
                float(
                    getattr(
                        account,
                        "equity",
                        0.0,
                    )
                    or 0.0
                ),

            "profit":
                float(
                    getattr(
                        account,
                        "profit",
                        0.0,
                    )
                    or 0.0
                ),

            "margin":
                float(
                    getattr(
                        account,
                        "margin",
                        0.0,
                    )
                    or 0.0
                ),

            "margin_free":
                float(
                    getattr(
                        account,
                        "margin_free",
                        0.0,
                    )
                    or 0.0
                ),

            "margin_level":
                float(
                    getattr(
                        account,
                        "margin_level",
                        0.0,
                    )
                    or 0.0
                ),

            "trade_allowed":
                bool(
                    getattr(
                        account,
                        "trade_allowed",
                        False,
                    )
                ),

            "trade_expert":
                bool(
                    getattr(
                        account,
                        "trade_expert",
                        False,
                    )
                ),

            "margin_mode":
                getattr(
                    account,
                    "margin_mode",
                    None,
                ),

            "raw":
                account,
        }

    except Exception:

        return None


def get_margin_mode() -> Optional[int]:

    try:

        account = get_account_info()

        if account is None:

            return None

        value = getattr(
            account,
            "margin_mode",
            None,
        )

        if value is None:

            return None

        return int(value)

    except Exception:

        return None


def get_account_trading_permissions() -> Dict[str, bool]:

    account = get_account_info()

    if account is None:

        return {

            "account_available":
                False,

            "trade_allowed":
                False,

            "trade_expert":
                False,

        }

    return {

        "account_available":
            True,

        "trade_allowed":
            bool(
                getattr(
                    account,
                    "trade_allowed",
                    False,
                )
            ),

        "trade_expert":
            bool(
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

def is_project_symbol(
    symbol: str,
) -> bool:

    return (
        str(symbol).strip().upper()
        == PILOT_SYMBOL.upper()
    )


def get_symbol_info(
    symbol: str = DEFAULT_SYMBOL,
):

    try:

        if not ensure_connection():

            return None

        if not is_project_symbol(symbol):

            return None

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return None

        return mt5.symbol_info(symbol)

    except Exception:

        return None


# ============================================================
# SYMBOL TICK
# ============================================================

def get_symbol_tick(
    symbol: str = DEFAULT_SYMBOL,
):

    try:

        if not ensure_connection():

            return None

        if not is_project_symbol(symbol):

            return None

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return None

        return mt5.symbol_info_tick(
            symbol
        )

    except Exception:

        return None


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(
    symbol: str = DEFAULT_SYMBOL,
) -> int:
    """
    Return broker-supported filling mode.
    """

    try:

        info = get_symbol_info(symbol)

        if info is None:

            return mt5.ORDER_FILLING_IOC

        filling_mode = int(
            getattr(
                info,
                "filling_mode",
                0,
            )
            or 0
        )

        # FOK
        if filling_mode & 1:

            return mt5.ORDER_FILLING_FOK

        # IOC
        if filling_mode & 2:

            return mt5.ORDER_FILLING_IOC

        # RETURN fallback
        return mt5.ORDER_FILLING_RETURN

    except Exception:

        return mt5.ORDER_FILLING_IOC


# ============================================================
# TIMEFRAME
# ============================================================

def _get_timeframe(
    timeframe: Any,
):

    mapping = {

        "1":
            mt5.TIMEFRAME_M1,

        "5":
            mt5.TIMEFRAME_M5,

        "15":
            mt5.TIMEFRAME_M15,

        "30":
            mt5.TIMEFRAME_M30,

        "60":
            mt5.TIMEFRAME_H1,

        "240":
            mt5.TIMEFRAME_H4,

        "1440":
            mt5.TIMEFRAME_D1,

        "M1":
            mt5.TIMEFRAME_M1,

        "M5":
            mt5.TIMEFRAME_M5,

        "M15":
            mt5.TIMEFRAME_M15,

        "M30":
            mt5.TIMEFRAME_M30,

        "H1":
            mt5.TIMEFRAME_H1,

        "H4":
            mt5.TIMEFRAME_H4,

        "D1":
            mt5.TIMEFRAME_D1,

        "D":
            mt5.TIMEFRAME_D1,
    }

    if isinstance(
        timeframe,
        int,
    ):

        return timeframe

    return mapping.get(
        str(timeframe).strip(),
        mt5.TIMEFRAME_M15,
    )


# ============================================================
# MARKET DATA
# ============================================================

def get_rates(
    symbol: str = DEFAULT_SYMBOL,
    timeframe: Any = "15",
    count: int = 100,
):

    try:

        if not ensure_connection():

            return []

        if not is_project_symbol(symbol):

            return []

        if not mt5.symbol_select(
            symbol,
            True,
        ):

            return []

        rates = mt5.copy_rates_from_pos(
            symbol,
            _get_timeframe(timeframe),
            0,
            int(count),
        )

        if rates is None:

            return []

        return rates

    except Exception:

        return []


# ============================================================
# PRICE NORMALIZATION
# ============================================================

def normalize_price(
    symbol: str,
    price: float,
) -> float:

    try:

        info = get_symbol_info(symbol)

        if info is None:

            return float(price)

        digits = int(
            getattr(
                info,
                "digits",
                2,
            )
            or 2
        )

        return round(
            float(price),
            digits,
        )

    except Exception:

        return float(price)


# ============================================================
# VOLUME NORMALIZATION
# ============================================================

def normalize_volume(
    symbol: str,
    volume: float,
) -> float:
    """
    Normalize volume to broker step while enforcing the
    project hard ceiling of 0.03 lots.

    This function never increases a requested volume above
    the requested project risk limit.
    """

    try:

        if not is_project_symbol(symbol):

            return 0.0

        requested = float(volume)

        if not math.isfinite(requested):

            return 0.0

        if requested < MIN_PROJECT_LOT:

            return 0.0

        if requested > MAX_PROJECT_LOT:

            return 0.0

        info = get_symbol_info(symbol)

        if info is None:

            return 0.0

        minimum = float(
            getattr(
                info,
                "volume_min",
                MIN_PROJECT_LOT,
            )
            or MIN_PROJECT_LOT
        )

        maximum = float(
            getattr(
                info,
                "volume_max",
                MAX_PROJECT_LOT,
            )
            or MAX_PROJECT_LOT
        )

        step = float(
            getattr(
                info,
                "volume_step",
                0.01,
            )
            or 0.01
        )

        if step <= 0:

            return 0.0

        if minimum > MAX_PROJECT_LOT:

            return 0.0

        broker_max = min(
            maximum,
            MAX_PROJECT_LOT,
        )

        if requested > broker_max:

            return 0.0

        normalized = (
            math.floor(
                requested / step
            )
            * step
        )

        if normalized < minimum:

            normalized = minimum

        if normalized > broker_max:

            return 0.0

        if normalized < MIN_PROJECT_LOT:

            return 0.0

        return round(
            normalized,
            2,
        )

    except Exception:

        return 0.0


# ============================================================
# STOP / FREEZE DISTANCE
# ============================================================

def get_min_stop_distance(
    symbol: str = DEFAULT_SYMBOL,
) -> float:

    try:

        info = get_symbol_info(symbol)

        if info is None:

            return 0.0

        point = float(
            getattr(
                info,
                "point",
                0.0,
            )
            or 0.0
        )

        stops_level = int(
            getattr(
                info,
                "trade_stops_level",
                0,
            )
            or 0
        )

        freeze_level = int(
            getattr(
                info,
                "trade_freeze_level",
                0,
            )
            or 0
        )

        level = max(
            stops_level,
            freeze_level,
        )

        return float(
            level * point
        )

    except Exception:

        return 0.0


def validate_order_levels(
    symbol: str,
    side: str,
    entry: float,
    sl: Optional[float],
    tp: Optional[float],
) -> Dict[str, Any]:
    """
    Validate price direction and broker stop/freeze distance.
    """

    try:

        side = str(
            side
        ).upper().strip()

        entry = float(entry)

        if entry <= 0:

            return {

                "valid":
                    False,

                "error":
                    "INVALID_ENTRY",

            }

        if side not in {
            "BUY",
            "SELL",
        }:

            return {

                "valid":
                    False,

                "error":
                    "INVALID_SIDE",

            }

        if sl is not None:

            sl = float(sl)

        if tp is not None:

            tp = float(tp)

        if side == "BUY":

            if sl is not None and not (
                sl < entry
            ):

                return {

                    "valid":
                        False,

                    "error":
                        "BUY_SL_DIRECTION_INVALID",

                }

            if tp is not None and not (
                tp > entry
            ):

                return {

                    "valid":
                        False,

                    "error":
                        "BUY_TP_DIRECTION_INVALID",

                }

        else:

            if sl is not None and not (
                sl > entry
            ):

                return {

                    "valid":
                        False,

                    "error":
                        "SELL_SL_DIRECTION_INVALID",

                }

            if tp is not None and not (
                tp < entry
            ):

                return {

                    "valid":
                        False,

                    "error":
                        "SELL_TP_DIRECTION_INVALID",

                }

        minimum_distance = (
            get_min_stop_distance(symbol)
        )

        if minimum_distance > 0:

            if sl is not None:

                if abs(entry - sl) < minimum_distance:

                    return {

                        "valid":
                            False,

                        "error":
                            "SL_TOO_CLOSE",

                        "minimum_distance":
                            minimum_distance,

                    }

            if tp is not None:

                if abs(entry - tp) < minimum_distance:

                    return {

                        "valid":
                            False,

                        "error":
                            "TP_TOO_CLOSE",

                        "minimum_distance":
                            minimum_distance,

                    }

        return {

            "valid":
                True,

            "error":
                None,

            "minimum_distance":
                minimum_distance,

        }

    except Exception as exc:

        return {

            "valid":
                False,

            "error":
                f"LEVEL_VALIDATION_ERROR:{exc}",

        }


# ============================================================
# POSITIONS
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None,
):

    try:

        if not ensure_connection():

            return []

        if symbol is not None:

            if not is_project_symbol(symbol):

                return []

            positions = mt5.positions_get(
                symbol=symbol
            )

        else:

            positions = mt5.positions_get()

        if not positions:

            return []

        return list(positions)

    except Exception:

        return []


def get_project_positions(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
):

    try:

        if not is_project_symbol(symbol):

            return []

        positions = get_open_positions(
            symbol
        )

        result = []

        for position in positions:

            position_magic = int(
                getattr(
                    position,
                    "magic",
                    0,
                )
                or 0
            )

            if position_magic != int(magic):

                continue

            result.append(
                position
            )

        return result

    except Exception:

        return []


def get_open_position_count(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
) -> int:

    try:

        return len(
            get_project_positions(
                symbol=symbol,
                magic=magic,
            )
        )

    except Exception:

        return PROJECT_MAX_POSITIONS


def validate_position_limit(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
) -> Dict[str, Any]:

    count = get_open_position_count(
        symbol=symbol,
        magic=magic,
    )

    if count >= PROJECT_MAX_POSITIONS:

        return {

            "valid":
                False,

            "error":
                "MAX_OPEN_POSITIONS_REACHED",

            "count":
                count,

            "max":
                PROJECT_MAX_POSITIONS,

        }

    return {

        "valid":
            True,

        "error":
            None,

        "count":
            count,

        "max":
            PROJECT_MAX_POSITIONS,

    }


# ============================================================
# MARGIN
# ============================================================

def calculate_order_margin(
    symbol: str,
    side: str,
    volume: float,
    price: Optional[float] = None,
) -> Optional[float]:

    try:

        if not ensure_connection():

            return None

        if not is_project_symbol(symbol):

            return None

        side = str(
            side
        ).upper().strip()

        if side == "BUY":

            order_type = mt5.ORDER_TYPE_BUY

        elif side == "SELL":

            order_type = mt5.ORDER_TYPE_SELL

        else:

            return None

        if price is None:

            tick = get_symbol_tick(
                symbol
            )

            if tick is None:

                return None

            price = (
                float(tick.ask)
                if side == "BUY"
                else float(tick.bid)
            )

        margin = mt5.order_calc_margin(
            order_type,
            symbol,
            float(volume),
            float(price),
        )

        if margin is None:

            return None

        return float(margin)

    except Exception:

        return None


def validate_free_margin(
    symbol: str,
    side: str,
    volume: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:

    try:

        account = get_account_info()

        if account is None:

            return {

                "valid":
                    False,

                "error":
                    "ACCOUNT_INFO_UNAVAILABLE",

            }

        free_margin = float(
            getattr(
                account,
                "margin_free",
                0.0,
            )
            or 0.0
        )

        required_margin = (
            calculate_order_margin(
                symbol,
                side,
                volume,
                price,
            )
        )

        if required_margin is None:

            return {

                "valid":
                    False,

                "error":
                    "MARGIN_CALCULATION_FAILED",

            }

        if free_margin <= 0:

            return {

                "valid":
                    False,

                "error":
                    "NO_FREE_MARGIN",

                "free_margin":
                    free_margin,

                "required_margin":
                    required_margin,

            }

        if required_margin > free_margin:

            return {

                "valid":
                    False,

                "error":
                    "INSUFFICIENT_FREE_MARGIN",

                "free_margin":
                    free_margin,

                "required_margin":
                    required_margin,

            }

        return {

            "valid":
                True,

            "error":
                None,

            "free_margin":
                free_margin,

            "required_margin":
                required_margin,

        }

    except Exception as exc:

        return {

            "valid":
                False,

            "error":
                f"MARGIN_VALIDATION_ERROR:{exc}",

        }


# ============================================================
# ORDER CHECK REQUEST
# ============================================================

def _get_order_type(
    side: str,
):

    side = str(
        side
    ).upper().strip()

    if side == "BUY":

        return mt5.ORDER_TYPE_BUY

    if side == "SELL":

        return mt5.ORDER_TYPE_SELL

    return None


def _build_market_request(
    symbol: str,
    side: str,
    volume: float,
    sl: Optional[float],
    tp: Optional[float],
    magic: int,
    deviation: int,
    comment: str,
) -> Optional[Dict[str, Any]]:

    try:

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            return None

        order_type = _get_order_type(
            side
        )

        if order_type is None:

            return None

        price = (
            float(tick.ask)
            if side == "BUY"
            else float(tick.bid)
        )

        price = normalize_price(
            symbol,
            price,
        )

        if sl is not None:

            sl = normalize_price(
                symbol,
                sl,
            )

        if tp is not None:

            tp = normalize_price(
                symbol,
                tp,
            )

        filling_mode = (
            get_filling_mode(symbol)
        )

        request = {

            "action":
                mt5.TRADE_ACTION_DEAL,

            "symbol":
                symbol,

            "volume":
                float(volume),

            "type":
                order_type,

            "price":
                price,

            "deviation":
                int(deviation),

            "magic":
                int(magic),

            "comment":
                str(comment),

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode,

        }

        if sl is not None:

            request["sl"] = sl

        if tp is not None:

            request["tp"] = tp

        return request

    except Exception:

        return None


# ============================================================
# FINAL PRE-FLIGHT SAFETY GATE
# ============================================================

def check_market_order(
    symbol: str,
    side: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    magic: int = DEFAULT_MAGIC,
    deviation: int = DEFAULT_DEVIATION,
    comment: str = DEFAULT_COMMENT,
) -> Dict[str, Any]:
    """
    Central final safety gate.

    IMPORTANT:
    This function does NOT send an order.

    It validates the order and runs mt5.order_check().
    """

    try:

        # ----------------------------------------------------
        # Connection
        # ----------------------------------------------------

        if not ensure_connection():

            return {

                "valid":
                    False,

                "error":
                    "MT5_NOT_CONNECTED",

            }

        # ----------------------------------------------------
        # Live gate
        # ----------------------------------------------------

        if not live_trading_allowed():

            return {

                "valid":
                    False,

                "error":
                    "LIVE_TRADING_DISABLED",

                "paper_trading":
                    bool(PAPER_TRADING),

                "allow_live_trading":
                    bool(ALLOW_LIVE_TRADING),

            }

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if not is_project_symbol(symbol):

            return {

                "valid":
                    False,

                "error":
                    "SYMBOL_NOT_ALLOWED",

                "expected":
                    PILOT_SYMBOL,

                "received":
                    symbol,

            }

        # ----------------------------------------------------
        # Account
        # ----------------------------------------------------

        account = get_account_info()

        if account is None:

            return {

                "valid":
                    False,

                "error":
                    "ACCOUNT_INFO_UNAVAILABLE",

            }

        if not bool(
            getattr(
                account,
                "trade_allowed",
                False,
            )
        ):

            return {

                "valid":
                    False,

                "error":
                    "ACCOUNT_TRADE_NOT_ALLOWED",

            }

        if not bool(
            getattr(
                account,
                "trade_expert",
                False,
            )
        ):

            return {

                "valid":
                    False,

                "error":
                    "ACCOUNT_EXPERT_NOT_ALLOWED",

            }

        # ----------------------------------------------------
        # Position limit
        # ----------------------------------------------------

        position_check = (
            validate_position_limit(
                symbol=symbol,
                magic=magic,
            )
        )

        if not position_check["valid"]:

            return position_check

        # ----------------------------------------------------
        # Volume
        # ----------------------------------------------------

        requested_volume = float(
            volume
        )

        if requested_volume < MIN_PROJECT_LOT:

            return {

                "valid":
                    False,

                "error":
                    "LOT_BELOW_PROJECT_MIN",

                "minimum":
                    MIN_PROJECT_LOT,

                "requested":
                    requested_volume,

            }

        if requested_volume > MAX_PROJECT_LOT:

            return {

                "valid":
                    False,

                "error":
                    "LOT_ABOVE_PROJECT_MAX",

                "maximum":
                    MAX_PROJECT_LOT,

                "requested":
                    requested_volume,

            }

        normalized_volume = (
            normalize_volume(
                symbol,
                requested_volume,
            )
        )

        if normalized_volume <= 0:

            return {

                "valid":
                    False,

                "error":
                    "INVALID_BROKER_VOLUME",

            }

        # ----------------------------------------------------
        # Tick / entry
        # ----------------------------------------------------

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            return {

                "valid":
                    False,

                "error":
                    "NO_TICK",

            }

        side = str(
            side
        ).upper().strip()

        if side == "BUY":

            entry = float(
                tick.ask
            )

        elif side == "SELL":

            entry = float(
                tick.bid
            )

        else:

            return {

                "valid":
                    False,

                "error":
                    "INVALID_SIDE",

            }

        # ----------------------------------------------------
        # SL / TP
        # ----------------------------------------------------

        levels = validate_order_levels(
            symbol=symbol,
            side=side,
            entry=entry,
            sl=sl,
            tp=tp,
        )

        if not levels["valid"]:

            return levels

        # ----------------------------------------------------
        # Margin
        # ----------------------------------------------------

        margin_check = (
            validate_free_margin(
                symbol=symbol,
                side=side,
                volume=normalized_volume,
                price=entry,
            )
        )

        if not margin_check["valid"]:

            return margin_check

        # ----------------------------------------------------
        # Request
        # ----------------------------------------------------

        request = _build_market_request(
            symbol=symbol,
            side=side,
            volume=normalized_volume,
            sl=sl,
            tp=tp,
            magic=magic,
            deviation=deviation,
            comment=comment,
        )

        if request is None:

            return {

                "valid":
                    False,

                "error":
                    "REQUEST_BUILD_FAILED",

            }

        # ----------------------------------------------------
        # MT5 ORDER CHECK
        # ----------------------------------------------------

        check_result = mt5.order_check(
            request
        )

        if check_result is None:

            return {

                "valid":
                    False,

                "error":
                    "ORDER_CHECK_RETURNED_NONE",

                "last_error":
                    str(
                        mt5.last_error()
                    ),

                "request":
                    request,

            }

        check_retcode = int(
            getattr(
                check_result,
                "retcode",
                0,
            )
            or 0
        )

        if check_retcode != 0:

            return {

                "valid":
                    False,

                "error":
                    "ORDER_CHECK_FAILED",

                "retcode":
                    check_retcode,

                "result":
                    check_result,

                "request":
                    request,

            }

        return {

            "valid":
                True,

            "error":
                None,

            "request":
                request,

            "order_check":
                check_result,

            "entry":
                entry,

            "volume":
                normalized_volume,

            "position_count":
                position_check["count"],

            "position_limit":
                position_check["max"],

            "margin":
                margin_check,

        }

    except Exception as exc:

        return {

            "valid":
                False,

            "error":
                f"ORDER_PREFLIGHT_EXCEPTION:{exc}",

        }


# ============================================================
# MARKET ORDER
# ============================================================

def send_market_order(
    symbol: str,
    side: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    magic: int = DEFAULT_MAGIC,
    deviation: int = DEFAULT_DEVIATION,
    comment: str = DEFAULT_COMMENT,
) -> Dict[str, Any]:
    """
    Send exactly one live market order after passing the final
    safety gate.

    No automatic retry is performed after order_send().
    """

    try:

        # ----------------------------------------------------
        # FINAL SAFETY GATE
        # ----------------------------------------------------

        preflight = check_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            deviation=deviation,
            comment=comment,
        )

        if not preflight["valid"]:

            return {

                "success":
                    False,

                "stage":
                    "PRE_FLIGHT",

                "error":
                    preflight.get(
                        "error"
                    ),

                "preflight":
                    preflight,

                "retcode":
                    None,

            }

        request = preflight[
            "request"
        ]

        # ----------------------------------------------------
        # ONE AND ONLY ONE SEND
        # ----------------------------------------------------

        result = mt5.order_send(
            request
        )

        # ----------------------------------------------------
        # Ambiguous response
        # ----------------------------------------------------

        if result is None:

            return {

                "success":
                    False,

                "ambiguous":
                    True,

                "stage":
                    "ORDER_SEND",

                "error":
                    str(
                        mt5.last_error()
                    ),

                "retcode":
                    None,

                "result":
                    None,

            }

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        retcode = int(
            getattr(
                result,
                "retcode",
                0,
            )
            or 0
        )

        success_codes = {

            mt5.TRADE_RETCODE_DONE,

            mt5.TRADE_RETCODE_DONE_PARTIAL,

        }

        success = (
            retcode
            in success_codes
        )

        return {

            "success":
                success,

            "ambiguous":
                False,

            "stage":
                "ORDER_SEND",

            "retcode":
                retcode,

            "order":
                getattr(
                    result,
                    "order",
                    None,
                ),

            "deal":
                getattr(
                    result,
                    "deal",
                    None,
                ),

            "volume":
                request.get(
                    "volume"
                ),

            "price":
                request.get(
                    "price"
                ),

            "sl":
                request.get(
                    "sl"
                ),

            "tp":
                request.get(
                    "tp"
                ),

            "symbol":
                request.get(
                    "symbol"
                ),

            "magic":
                request.get(
                    "magic"
                ),

            "result":
                result,

            "preflight":
                preflight,

            "error":
                None
                if success
                else str(result),

        }

    except Exception as exc:

        return {

            "success":
                False,

            "ambiguous":
                False,

            "stage":
                "EXCEPTION",

            "error":
                str(exc),

            "retcode":
                None,

        }


# ============================================================
# UPDATE TRADE STATUS
# ============================================================

def update_trade_status(
    trade_id: Any,
    status: str,
    **kwargs: Any,
) -> bool:

    try:

        try:

            from core.database_manager import (
                update_trade_status as db_update_trade_status,
            )

            result = db_update_trade_status(
                trade_id,
                status,
                **kwargs,
            )

            return bool(
                result
                if result is not None
                else True
            )

        except (
            ImportError,
            AttributeError,
            TypeError,
        ):

            pass

        try:

            from database import (
                update_trade_status as legacy_update_trade_status,
            )

            result = legacy_update_trade_status(
                trade_id,
                status,
                **kwargs,
            )

            return bool(
                result
                if result is not None
                else True
            )

        except (
            ImportError,
            AttributeError,
            TypeError,
        ):

            pass

        return True

    except Exception:

        return False


# ============================================================
# MT5 CONNECTOR CLASS
# ============================================================

class MT5Connector:

    def __init__(self):

        self.initialized = False

    def initialize(
        self,
        password: Optional[str] = None,
    ) -> bool:

        self.initialized = initialize_mt5(
            password
        )

        return self.initialized

    def shutdown(self) -> None:

        shutdown_mt5()

        self.initialized = False

    def is_connected(self) -> bool:

        return is_connected()

    def get_account_info(self):

        return get_account_info()

    def get_account_snapshot(self):

        return get_account_snapshot()

    def get_margin_mode(self):

        return get_margin_mode()

    def get_account_trading_permissions(self):

        return get_account_trading_permissions()

    def get_symbol_info(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):

        return get_symbol_info(
            symbol
        )

    def get_symbol_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):

        return get_symbol_tick(
            symbol
        )

    def get_filling_mode(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> int:

        return get_filling_mode(
            symbol
        )

    def get_rates(
        self,
        symbol: str = DEFAULT_SYMBOL,
        timeframe: Any = "15",
        count: int = 100,
    ):

        return get_rates(
            symbol,
            timeframe,
            count,
        )

    def normalize_price(
        self,
        symbol: str,
        price: float,
    ) -> float:

        return normalize_price(
            symbol,
            price,
        )

    def normalize_volume(
        self,
        symbol: str,
        volume: float,
    ) -> float:

        return normalize_volume(
            symbol,
            volume,
        )

    def get_min_stop_distance(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> float:

        return get_min_stop_distance(
            symbol
        )

    def validate_order_levels(
        self,
        symbol: str,
        side: str,
        entry: float,
        sl: Optional[float],
        tp: Optional[float],
    ):

        return validate_order_levels(
            symbol=symbol,
            side=side,
            entry=entry,
            sl=sl,
            tp=tp,
        )

    def get_open_positions(
        self,
        symbol: Optional[str] = None,
    ):

        return get_open_positions(
            symbol
        )

    def get_project_positions(
        self,
        symbol: str = PILOT_SYMBOL,
        magic: int = DEFAULT_MAGIC,
    ):

        return get_project_positions(
            symbol=symbol,
            magic=magic,
        )

    def get_open_position_count(
        self,
        symbol: str = PILOT_SYMBOL,
        magic: int = DEFAULT_MAGIC,
    ) -> int:

        return get_open_position_count(
            symbol=symbol,
            magic=magic,
        )

    def calculate_order_margin(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: Optional[float] = None,
    ):

        return calculate_order_margin(
            symbol=symbol,
            side=side,
            volume=volume,
            price=price,
        )

    def validate_free_margin(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: Optional[float] = None,
    ):

        return validate_free_margin(
            symbol=symbol,
            side=side,
            volume=volume,
            price=price,
        )

    def check_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        magic: int = DEFAULT_MAGIC,
        deviation: int = DEFAULT_DEVIATION,
        comment: str = DEFAULT_COMMENT,
    ):

        return check_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            deviation=deviation,
            comment=comment,
        )

    def send_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        magic: int = DEFAULT_MAGIC,
        deviation: int = DEFAULT_DEVIATION,
        comment: str = DEFAULT_COMMENT,
    ):

        return send_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            deviation=deviation,
            comment=comment,
        )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "MT5Connector",

    "PILOT_SYMBOL",

    "DEFAULT_SYMBOL",

    "DEFAULT_MAGIC",

    "DEFAULT_DEVIATION",

    "DEFAULT_COMMENT",

    "MIN_PROJECT_LOT",

    "MAX_PROJECT_LOT",

    "PROJECT_MAX_POSITIONS",

    "get_terminal_path",

    "live_trading_allowed",

    "initialize_mt5",

    "ensure_connection",

    "shutdown_mt5",

    "is_connected",

    "get_account_info",

    "get_account_snapshot",

    "get_margin_mode",

    "get_account_trading_permissions",

    "is_project_symbol",

    "get_symbol_info",

    "get_symbol_tick",

    "get_filling_mode",

    "_get_timeframe",

    "get_rates",

    "normalize_price",

    "normalize_volume",

    "get_min_stop_distance",

    "validate_order_levels",

    "get_open_positions",

    "get_project_positions",

    "get_open_position_count",

    "validate_position_limit",

    "calculate_order_margin",

    "validate_free_margin",

    "check_market_order",

    "send_market_order",

    "update_trade_status",

]
