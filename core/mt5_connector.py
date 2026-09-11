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
    Return the configured MT5 terminal path.
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

    Live trading is allowed ONLY when:

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

    The authenticated portable terminal is used directly.
    No forced Python login is performed.
    """

    if platform.system().lower() != "windows":
        return False

    terminal_path = get_terminal_path()

    try:
        try:
            mt5.shutdown()
        except Exception:
            pass

        initialized = mt5.initialize(
            path=terminal_path,
            portable=True,
            timeout=MT5_TIMEOUT,
        )

        if not initialized:
            return False

        terminal_info = mt5.terminal_info()

        if terminal_info is None:
            try:
                mt5.shutdown()
            except Exception:
                pass

            return False

        if not bool(
            getattr(
                terminal_info,
                "connected",
                False,
            )
        ):
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

    One controlled initialization attempt is made when
    the current connection is unavailable.
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
    Return the live MT5 account state.

    No hardcoded balance is used for risk calculations.
    """

    try:
        account = get_account_info()

        if account is None:
            return None

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
                or 0.0
            ),

            "equity": float(
                getattr(
                    account,
                    "equity",
                    0.0,
                )
                or 0.0
            ),

            "profit": float(
                getattr(
                    account,
                    "profit",
                    0.0,
                )
                or 0.0
            ),

            "margin": float(
                getattr(
                    account,
                    "margin",
                    0.0,
                )
                or 0.0
            ),

            "margin_free": float(
                getattr(
                    account,
                    "margin_free",
                    0.0,
                )
                or 0.0
            ),

            "margin_level": float(
                getattr(
                    account,
                    "margin_level",
                    0.0,
                )
                or 0.0
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

            "margin_mode": getattr(
                account,
                "margin_mode",
                None,
            ),

            "raw": account,
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
    Determine a broker-supported filling mode.

    SYMBOL_FILLING_FOK = 1
    SYMBOL_FILLING_IOC = 2
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

        # Broker supports FOK.
        if filling_mode & 1:
            return mt5.ORDER_FILLING_FOK

        # Broker supports IOC.
        if filling_mode & 2:
            return mt5.ORDER_FILLING_IOC

        # RETURN fallback.
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
        "1": mt5.TIMEFRAME_M1,
        "5": mt5.TIMEFRAME_M5,
        "15": mt5.TIMEFRAME_M15,
        "30": mt5.TIMEFRAME_M30,
        "60": mt5.TIMEFRAME_H1,
        "240": mt5.TIMEFRAME_H4,
        "1440": mt5.TIMEFRAME_D1,

        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "D": mt5.TIMEFRAME_D1,
    }

    if isinstance(
        timeframe,
        int,
    ):
        return timeframe

    return mapping.get(
        str(timeframe).strip().upper(),
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
    Normalize requested volume to the broker step.

    IMPORTANT:
    This function never silently increases or decreases a
    project request above the project risk ceiling.

    A request above 0.03 returns 0.0 and must be rejected.
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

        broker_min = float(
            getattr(
                info,
                "volume_min",
                MIN_PROJECT_LOT,
            )
            or MIN_PROJECT_LOT
        )

        broker_max = float(
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

        if broker_min > MAX_PROJECT_LOT:
            return 0.0

        allowed_max = min(
            broker_max,
            MAX_PROJECT_LOT,
        )

        if requested > allowed_max:
            return 0.0

        # Normalize DOWN to broker step.
        normalized = (
            math.floor(
                requested / step
            )
            * step
        )

        if normalized < broker_min:
            normalized = broker_min

        if normalized < MIN_PROJECT_LOT:
            return 0.0

        if normalized > allowed_max:
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
    Validate SL/TP direction and broker stop/freeze distance.
    """

    try:
        side = str(
            side
        ).upper().strip()

        entry = float(entry)

        if entry <= 0:
            return {
                "valid": False,
                "error": "INVALID_ENTRY",
            }

        if side not in {
            "BUY",
            "SELL",
        }:
            return {
                "valid": False,
                "error": "INVALID_SIDE",
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
                    "valid": False,
                    "error": "BUY_SL_DIRECTION_INVALID",
                }

            if tp is not None and not (
                tp > entry
            ):
                return {
                    "valid": False,
                    "error": "BUY_TP_DIRECTION_INVALID",
                }

        else:

            if sl is not None and not (
                sl > entry
            ):
                return {
                    "valid": False,
                    "error": "SELL_SL_DIRECTION_INVALID",
                }

            if tp is not None and not (
                tp < entry
            ):
                return {
                    "valid": False,
                    "error": "SELL_TP_DIRECTION_INVALID",
                }

        minimum_distance = (
            get_min_stop_distance(symbol)
        )

        if minimum_distance > 0:

            if sl is not None:
                if abs(entry - sl) < minimum_distance:
                    return {
                        "valid": False,
                        "error": "SL_TOO_CLOSE",
                        "minimum_distance": minimum_distance,
                    }

            if tp is not None:
                if abs(entry - tp) < minimum_distance:
                    return {
                        "valid": False,
                        "error": "TP_TOO_CLOSE",
                        "minimum_distance": minimum_distance,
                    }

        return {
            "valid": True,
            "error": None,
            "minimum_distance": minimum_distance,
        }

    except Exception as exc:
        return {
            "valid": False,
            "error": f"LEVEL_VALIDATION_ERROR:{exc}",
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

        if positions is None:
            return []

        return list(positions)

    except Exception:
        return []


def get_project_positions(
    symbol: str = PILOT_SYMBOL,
    magic: int = DEFAULT_MAGIC,
):
    """
    Return only positions belonging to the project.

    Filtering:
        Symbol == XAUUSD.su
        Magic == 20260731
    """

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

            result.append(position)

        return result

    except Exception:
        return []


def get_open_position_count(
    symbol: Optional[str] = PILOT_SYMBOL,
    magic: Optional[int] = DEFAULT_MAGIC,
) -> int:
    """
    Count project positions.

    When magic is supplied, only project positions with that
    magic number are counted.

    Fail-closed:
        If a project position query cannot be trusted, the
        configured maximum is returned.
    """

    try:

        if symbol is not None and not is_project_symbol(symbol):
            return PROJECT_MAX_POSITIONS

        positions = get_open_positions(
            symbol
        )

        if magic is None:
            return len(positions)

        count = 0

        for position in positions:

            position_magic = int(
                getattr(
                    position,
                    "magic",
                    0,
                )
                or 0
            )

            if position_magic == int(magic):
                count += 1

        return count

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
            "valid": False,
            "error": "MAX_OPEN_POSITIONS_REACHED",
            "count": count,
            "max": PROJECT_MAX_POSITIONS,
        }

    return {
        "valid": True,
        "error": None,
        "count": count,
        "max": PROJECT_MAX_POSITIONS,
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
                "valid": False,
                "error": "ACCOUNT_INFO_UNAVAILABLE",
            }

        free_margin = float(
            getattr(
                account,
                "margin_free",
                0.0,
            )
            or 0.0
        )

        required_margin = calculate_order_margin(
            symbol,
            side,
            volume,
            price,
        )

        if required_margin is None:
            return {
                "valid": False,
                "error": "MARGIN_CALCULATION_FAILED",
            }

        if free_margin <= 0:
            return {
                "valid": False,
                "error": "NO_FREE_MARGIN",
                "free_margin": free_margin,
                "required_margin": required_margin,
            }

        if required_margin > free_margin:
            return {
                "valid": False,
                "error": "INSUFFICIENT_FREE_MARGIN",
                "free_margin": free_margin,
                "required_margin": required_margin,
            }

        return {
            "valid": True,
            "error": None,
            "free_margin": free_margin,
            "required_margin": required_margin,
        }

    except Exception as exc:
        return {
            "valid": False,
            "error": f
