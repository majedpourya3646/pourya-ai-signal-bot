# core/mt5_connector.py
# Pourya Trader AI
# MT5 Connector - Safe Integration Layer
# Version: 2.2.0-MT5-SAFE

from __future__ import annotations

import math
import os
import platform
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Union

import MetaTrader5 as mt5


# ============================================================
# CONFIG
# ============================================================

try:
    from config import (
        ALLOW_LIVE_TRADING,
        DEFAULT_DEVIATION,
        DEFAULT_LOT,
        MAX_OPEN_TRADES,
        MAX_PROJECT_LOT,
        MIN_PROJECT_LOT,
        MT5_LOGIN,
        MT5_MAGIC_NUMBER,
        MT5_ORDER_COMMENT,
        MT5_PASSWORD,
        MT5_PORTABLE,
        MT5_SERVER,
        MT5_TERMINAL_PATH,
        MT5_TIMEOUT,
        PAPER_TRADING,
        PILOT_SYMBOL,
    )

except Exception:
    # Safe fallback values.
    # These are intentionally conservative.
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "815143"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "OtetGroup-MT5")

    MT5_TERMINAL_PATH = os.getenv(
        "MT5_TERMINAL_PATH",
        r"C:\MT5-Pourya\terminal64.exe",
    )

    MT5_PORTABLE = True
    MT5_TIMEOUT = 60000

    PILOT_SYMBOL = "XAUUSD.su"

    MAX_OPEN_TRADES = 5

    MIN_PROJECT_LOT = 0.01
    DEFAULT_LOT = 0.01
    MAX_PROJECT_LOT = 0.03

    DEFAULT_DEVIATION = 20
    MT5_MAGIC_NUMBER = 20260731
    MT5_ORDER_COMMENT = "Pourya Trader AI"

    PAPER_TRADING = True
    ALLOW_LIVE_TRADING = False


# ============================================================
# COMPATIBILITY CONSTANTS
# ============================================================

DEFAULT_SYMBOL = PILOT_SYMBOL
DEFAULT_MAGIC = MT5_MAGIC_NUMBER

MT5_PATH = MT5_TERMINAL_PATH
MT5_PORTABLE_MODE = MT5_PORTABLE
MT5_CONNECTION_TIMEOUT = MT5_TIMEOUT

PROJECT_MIN_LOT = MIN_PROJECT_LOT
PROJECT_DEFAULT_LOT = DEFAULT_LOT
PROJECT_MAX_LOT = MAX_PROJECT_LOT
MAX_PROJECT_POSITIONS = MAX_OPEN_TRADES


# ============================================================
# INTERNAL STATE
# ============================================================

_last_connection_check: Optional[datetime] = None
_last_connection_result: bool = False


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        if math.isfinite(result):
            return result
    except (TypeError, ValueError):
        pass

    return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_symbol(symbol: Optional[str]) -> str:
    symbol = (symbol or PILOT_SYMBOL).strip()

    if not symbol:
        return PILOT_SYMBOL

    return symbol


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_mt5(
    password: Optional[str] = None,
    login: Optional[int] = None,
    server: Optional[str] = None,
) -> bool:
    """
    Initialize the exact portable MT5 terminal used by Pourya Trader AI.
    """

    global _last_connection_check
    global _last_connection_result

    if platform.system().lower() != "windows":
        _last_connection_check = datetime.now()
        _last_connection_result = False
        return False

    terminal_path = MT5_TERMINAL_PATH

    login_value = (
        _safe_int(login, MT5_LOGIN)
        if login is not None
        else MT5_LOGIN
    )

    password_value = (
        password
        if password is not None
        else MT5_PASSWORD
    )

    server_value = (
        server.strip()
        if isinstance(server, str) and server.strip()
        else MT5_SERVER
    )

    try:
        # Do not shutdown an existing valid connection unnecessarily.
        current_terminal = mt5.terminal_info()

        if current_terminal is not None:
            current_account = mt5.account_info()

            if current_account is not None:
                _last_connection_check = datetime.now()
                _last_connection_result = True
                return True

    except Exception:
        pass

    try:
        initialized = mt5.initialize(
            path=terminal_path,
            login=login_value if login_value else None,
            password=password_value if password_value else None,
            server=server_value if server_value else None,
            portable=bool(MT5_PORTABLE),
            timeout=int(MT5_TIMEOUT),
        )

    except TypeError:
        # Compatibility fallback for installations where
        # optional login/password/server arguments are problematic.
        try:
            initialized = mt5.initialize(
                path=terminal_path,
                portable=bool(MT5_PORTABLE),
                timeout=int(MT5_TIMEOUT),
            )
        except Exception:
            initialized = False

    except Exception:
        initialized = False

    _last_connection_check = datetime.now()
    _last_connection_result = bool(initialized)

    return bool(initialized)


def ensure_connection() -> bool:
    """
    Ensure MT5 is initialized and an account is available.
    """

    global _last_connection_check
    global _last_connection_result

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()

        if terminal is not None and account is not None:
            _last_connection_check = datetime.now()
            _last_connection_result = True
            return True
    except Exception:
        pass

    return initialize_mt5()


def shutdown_mt5() -> bool:
    """
    Safely shut down the MT5 Python connection.
    """

    global _last_connection_check
    global _last_connection_result

    try:
        mt5.shutdown()

        _last_connection_check = datetime.now()
        _last_connection_result = False

        return True

    except Exception:
        return False


def is_connected() -> bool:
    """
    Return True when MT5 terminal and account are accessible.
    """

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()

        return terminal is not None and account is not None

    except Exception:
        return False


# ============================================================
# TERMINAL / ACCOUNT INFORMATION
# ============================================================

def get_terminal_info() -> Optional[Any]:
    if not ensure_connection():
        return None

    try:
        return mt5.terminal_info()
    except Exception:
        return None


def get_terminal_permissions() -> Dict[str, Any]:
    """
    Return MT5 terminal/account trading permissions.
    """

    terminal = get_terminal_info()
    account = get_account_info()

    if terminal is None:
        return {
            "connected": False,
            "trade_allowed": False,
            "trade_expert": False,
            "dlls_allowed": False,
            "account_trade_allowed": False,
            "account_trade_expert": False,
        }

    return {
        "connected": True,
        "trade_allowed": bool(
            getattr(terminal, "trade_allowed", False)
        ),
        "trade_expert": bool(
            getattr(terminal, "trade_expert", False)
        ),
        "dlls_allowed": bool(
            getattr(terminal, "dlls_allowed", False)
        ),
        "account_trade_allowed": bool(
            getattr(account, "trade_allowed", False)
        ) if account is not None else False,
        "account_trade_expert": bool(
            getattr(account, "trade_expert", False)
        ) if account is not None else False,
    }


def get_account_info() -> Optional[Any]:
    """
    Return the native MT5 account_info object.
    """

    if not ensure_connection():
        return None

    try:
        return mt5.account_info()
    except Exception:
        return None


def get_account_snapshot() -> Dict[str, Any]:
    """
    Return a serializable account snapshot.
    """

    account = get_account_info()

    if account is None:
        return {
            "connected": False,
            "login": MT5_LOGIN,
            "server": MT5_SERVER,
            "balance": 0.0,
            "equity": 0.0,
            "credit": 0.0,
            "profit": 0.0,
            "margin": 0.0,
            "free_margin": 0.0,
            "margin_level": 0.0,
            "leverage": 0,
            "trade_allowed": False,
            "trade_expert": False,
        }

    return {
        "connected": True,
        "login": getattr(account, "login", MT5_LOGIN),
        "server": getattr(account, "server", MT5_SERVER),
        "balance": _safe_float(getattr(account, "balance", 0.0)),
        "equity": _safe_float(getattr(account, "equity", 0.0)),
        "credit": _safe_float(getattr(account, "credit", 0.0)),
        "profit": _safe_float(getattr(account, "profit", 0.0)),
        "margin": _safe_float(getattr(account, "margin", 0.0)),
        "free_margin": _safe_float(
            getattr(account, "margin_free", 0.0)
        ),
        "margin_level": _safe_float(
            getattr(account, "margin_level", 0.0)
        ),
        "leverage": _safe_int(
            getattr(account, "leverage", 0)
        ),
        "trade_allowed": bool(
            getattr(account, "trade_allowed", False)
        ),
        "trade_expert": bool(
            getattr(account, "trade_expert", False)
        ),
    }


def get_free_margin() -> float:
    account = get_account_info()

    if account is None:
        return 0.0

    return _safe_float(
        getattr(account, "margin_free", 0.0)
    )


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol: str = PILOT_SYMBOL,
) -> Optional[Any]:
    """
    Return native MT5 symbol information.
    """

    if not ensure_connection():
        return None

    symbol = _normalize_symbol(symbol)

    try:
        info = mt5.symbol_info(symbol)

        if info is None:
            return None

        if not getattr(info, "visible", True):
            try:
                mt5.symbol_select(symbol, True)
            except Exception:
                pass

            info = mt5.symbol_info(symbol)

        return info

    except Exception:
        return None


def get_symbol_tick(
    symbol: str = PILOT_SYMBOL,
) -> Optional[Any]:
    if not ensure_connection():
        return None

    symbol = _normalize_symbol(symbol)

    try:
        return mt5.symbol_info_tick(symbol)
    except Exception:
        return None


def get_rates(
    symbol: str = PILOT_SYMBOL,
    timeframe: int = mt5.TIMEFRAME_M15,
    count: int = 100,
) -> Any:
    """
    Return MT5 OHLCV rates.
    """

    if not ensure_connection():
        return None

    symbol = _normalize_symbol(symbol)
    count = max(1, int(count))

    try:
        return mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            count,
        )
    except Exception:
        return None


# ============================================================
# PRICE / VOLUME NORMALIZATION
# ============================================================

def normalize_price(
    price: Union[int, float],
    symbol: str = PILOT_SYMBOL,
) -> float:
    """
    Normalize price according to broker digits.
    """

    symbol = _normalize_symbol(symbol)
    info = get_symbol_info(symbol)

    value = _safe_float(price)

    if info is None:
        return round(value, 2)

    digits = _safe_int(
        getattr(info, "digits", 2),
        2,
    )

    return round(value, digits)


def normalize_volume(
    volume: Union[int, float],
    symbol: str = PILOT_SYMBOL,
) -> float:
    """
    Normalize volume according to broker min/max/step,
    while respecting the project's hard 0.01-0.03 lot ceiling.
    """

    requested = _safe_float(volume, DEFAULT_LOT)

    if requested <= 0:
        requested = DEFAULT_LOT

    info = get_symbol_info(symbol)

    broker_min = _safe_float(
        getattr(info, "volume_min", MIN_PROJECT_LOT)
        if info is not None
        else MIN_PROJECT_LOT,
        MIN_PROJECT_LOT,
    )

    broker_max = _safe_float(
        getattr(info, "volume_max", MAX_PROJECT_LOT)
        if info is not None
        else MAX_PROJECT_LOT,
        MAX_PROJECT_LOT,
    )

    broker_step = _safe_float(
        getattr(info, "volume_step", MIN_PROJECT_LOT)
        if info is not None
        else MIN_PROJECT_LOT,
        MIN_PROJECT_LOT,
    )

    if broker_step <= 0:
        broker_step = MIN_PROJECT_LOT

    effective_min = max(
        MIN_PROJECT_LOT,
        broker_min,
    )

    effective_max = min(
        MAX_PROJECT_LOT,
        broker_max,
    )

    if effective_max < effective_min:
        effective_max = effective_min

    requested = max(
        effective_min,
        min(requested, effective_max),
    )

    # Floor to broker step to avoid accidentally exceeding
    # the requested/project risk ceiling.
    steps = math.floor(
        (requested - effective_min + 1e-12)
        / broker_step
    )

    normalized = (
        effective_min
        + steps * broker_step
    )

    normalized = max(
        effective_min,
        min(normalized, effective_max),
    )

    # Most XAUUSD brokers use 0.01 volume precision.
    return round(normalized, 2)


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(
    symbol: str = PILOT_SYMBOL,
) -> int:
    """
    Determine a suitable MT5 order filling mode.
    """

    info = get_symbol_info(symbol)

    if info is None:
        return mt5.ORDER_FILLING_FOK

    filling_mode = getattr(
        info,
        "filling_mode",
        None,
    )

    # MT5 filling mode flags:
    # FOK = 1
    # IOC = 2
    # RETURN = 4
    #
    # Prefer FOK, then IOC, then RETURN.

    try:
        flags = int(filling_mode)

        if flags & 1:
            return mt5.ORDER_FILLING_FOK

        if flags & 2:
            return mt5.ORDER_FILLING_IOC

        if flags & 4:
            return mt5.ORDER_FILLING_RETURN

    except Exception:
        pass

    return mt5.ORDER_FILLING_FOK


# ============================================================
# POSITIONS
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None,
) -> List[Any]:
    """
    Return open positions.

    If symbol is omitted, return project positions belonging
    to Pourya Trader AI's magic number.
    """

    if not ensure_connection():
        return []

    try:
        if symbol:
            symbol = _normalize_symbol(symbol)
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()

        if not positions:
            return []

        result = []

        for position in positions:
            magic = _safe_int(
                getattr(position, "magic", 0),
                0,
            )

            if magic == int(MT5_MAGIC_NUMBER):
                result.append(position)

        return result

    except Exception:
        return []


def get_project_position_count() -> int:
    return len(get_open_positions())


def get_project_positions(
    symbol: Optional[str] = None,
) -> List[Any]:
    positions = get_open_positions(symbol)

    if symbol is None:
        return positions

    normalized = _normalize_symbol(symbol)

    return [
        position
        for position in positions
        if getattr(position, "symbol", "") == normalized
    ]


def has_open_direction(
    side: str,
    symbol: str = PILOT_SYMBOL,
) -> bool:
    """
    Prevent duplicate same-direction project positions.
    """

    side = str(side).strip().upper()

    if side not in {"BUY", "SELL"}:
        return False

    positions = get_project_positions(symbol)

    target_type = (
        mt5.POSITION_TYPE_BUY
        if side == "BUY"
        else mt5.POSITION_TYPE_SELL
    )

    for position in positions:
        if getattr(position, "type", None) == target_type:
            return True

    return False


# ============================================================
# RISK / DAILY LOSS
# ============================================================

def get_daily_loss_snapshot() -> Dict[str, Any]:
    """
    Return current account risk snapshot.

    NOTE:
    This is intentionally conservative. A persistent start-of-day
    baseline should be added later for production-grade daily loss
    accounting.
    """

    account = get_account_info()

    if account is None:
        return {
            "available": False,
            "balance": 0.0,
            "equity": 0.0,
            "profit": 0.0,
            "daily_loss": 0.0,
            "daily_loss_pct": 0.0,
            "within_limit": False,
        }

    balance = _safe_float(
        getattr(account, "balance", 0.0)
    )

    equity = _safe_float(
        getattr(account, "equity", 0.0)
    )

    profit = _safe_float(
        getattr(account, "profit", 0.0)
    )

    # For the current pilot account, equity is the safest
    # immediate capital figure.
    reference = max(
        abs(balance),
        abs(equity),
        1.0,
    )

    loss_amount = max(
        0.0,
        -profit,
    )

    loss_pct = (
        loss_amount / reference
    ) * 100.0

    # Project hard daily limit = 5%.
    within_limit = loss_pct < 5.0

    return {
        "available": True,
        "balance": balance,
        "equity": equity,
        "profit": profit,
        "daily_loss": loss_amount,
        "daily_loss_pct": loss_pct,
        "daily_loss_limit_pct": 5.0,
        "within_limit": within_limit,
    }


def validate_daily_loss_limit(
    max_daily_loss_pct: float = 5.0,
) -> Dict[str, Any]:
    snapshot = get_daily_loss_snapshot()

    if not snapshot.get("available", False):
        return {
            "valid": False,
            "reason": "Account information unavailable.",
            "snapshot": snapshot,
        }

    loss_pct = _safe_float(
        snapshot.get("daily_loss_pct", 0.0)
    )

    limit = _safe_float(
        max_daily_loss_pct,
        5.0,
    )

    valid = loss_pct < limit

    return {
        "valid": valid,
        "reason": (
            "Daily loss limit OK."
            if valid
            else "Daily loss limit exceeded."
        ),
        "daily_loss_pct": loss_pct,
        "limit_pct": limit,
        "snapshot": snapshot,
    }


# ============================================================
# POSITION LIMIT
# ============================================================

def validate_position_limit(
    max_positions: Optional[int] = None,
) -> Dict[str, Any]:
    limit = (
        int(max_positions)
        if max_positions is not None
        else int(MAX_OPEN_TRADES)
    )

    count = get_project_position_count()

    return {
        "valid": count < limit,
        "count": count,
        "limit": limit,
        "reason": (
            "Position limit OK."
            if count < limit
            else "Maximum project positions reached."
        ),
    }


# ============================================================
# MARGIN
# ============================================================

def calculate_margin(
    symbol: str,
    volume: float,
    order_type: int,
    price: Optional[float] = None,
) -> float:
    """
    Calculate estimated required margin.
    """

    if not ensure_connection():
        return 0.0

    symbol = _normalize_symbol(symbol)
    volume = normalize_volume(volume, symbol)

    if price is None:
        tick = get_symbol_tick(symbol)

        if tick is None:
            return 0.0

        if order_type == mt5.ORDER_TYPE_SELL:
            price = getattr(tick, "bid", 0.0)
        else:
            price = getattr(tick, "ask", 0.0)

    price = _safe_float(price)

    if price <= 0:
        return 0.0

    try:
        result = mt5.order_calc_margin(
            order_type,
            symbol,
            volume,
            price,
        )

        if result is None:
            return 0.0

        return max(0.0, _safe_float(result))

    except Exception:
        return 0.0


def validate_margin(
    symbol: str,
    volume: float,
    side: str,
) -> Dict[str, Any]:
    side = str(side).strip().upper()

    order_type = (
        mt5.ORDER_TYPE_BUY
        if side == "BUY"
        else mt5.ORDER_TYPE_SELL
    )

    required = calculate_margin(
        symbol=symbol,
        volume=volume,
        order_type=order_type,
    )

    free_margin = get_free_margin()

    # Keep an additional 20% safety buffer.
    safe_required = required * 1.20

    valid = (
        required > 0
        and free_margin >= safe_required
    )

    return {
        "valid": valid,
        "required_margin": required,
        "safe_required_margin": safe_required,
        "free_margin": free_margin,
        "reason": (
            "Margin OK."
            if valid
            else "Insufficient free margin."
        ),
    }


# ============================================================
# LIVE TRADING SAFETY
# ============================================================

def live_trading_allowed() -> bool:
    """
    Final hard safety switch.

    Live trading requires ALL of:
      - PAPER_TRADING == False
      - ALLOW_LIVE_TRADING == True
      - connected MT5
      - terminal trading allowed
      - expert trading allowed
      - account trading allowed
      - account expert trading allowed
    """

    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    permissions = get_terminal_permissions()

    if not permissions.get("connected", False):
        return False

    if not permissions.get("trade_allowed", False):
        return False

    if not permissions.get("trade_expert", False):
        return False

    if not permissions.get("account_trade_allowed", False):
        return False

    if not permissions.get("account_trade_expert", False):
        return False

    return True


def trading_safety_status() -> Dict[str, Any]:
    permissions = get_terminal_permissions()

    return {
        "paper_trading": bool(PAPER_TRADING),
        "allow_live_trading": bool(ALLOW_LIVE_TRADING),
        "live_trading_allowed": live_trading_allowed(),
        "permissions": permissions,
        "pilot_symbol": PILOT_SYMBOL,
        "max_open_trades": MAX_OPEN_TRADES,
        "min_lot": MIN_PROJECT_LOT,
        "default_lot": DEFAULT_LOT,
        "max_lot": MAX_PROJECT_LOT,
    }


# ============================================================
# ORDER CHECK
# ============================================================

def order_check(
    symbol: str,
    side: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    deviation: int = DEFAULT_DEVIATION,
) -> Dict[str, Any]:
    """
    Perform MT5 order_check without sending an order.
    """

    if not ensure_connection():
        return {
            "valid": False,
            "retcode": None,
            "comment": "MT5 connection unavailable.",
            "request": None,
        }

    symbol = _normalize_symbol(symbol)
    side = str(side).strip().upper()

    if symbol != PILOT_SYMBOL:
        return {
            "valid": False,
            "retcode": None,
            "comment": (
                f"Only pilot symbol {PILOT_SYMBOL} "
                f"is allowed."
            ),
            "request": None,
        }

    if side not in {"BUY", "SELL"}:
        return {
            "valid": False,
            "retcode": None,
            "comment": "Invalid order side.",
            "request": None,
        }

    tick = get_symbol_tick(symbol)

    if tick is None:
        return {
            "valid": False,
            "retcode": None,
            "comment": "Symbol tick unavailable.",
            "request": None,
        }

    volume = normalize_volume(volume, symbol)

    if side == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = _safe_float(
            getattr(tick, "ask", 0.0)
        )
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = _safe_float(
            getattr(tick, "bid", 0.0)
        )

    if price <= 0:
        return {
            "valid": False,
            "retcode": None,
            "comment": "Invalid market price.",
            "request": None,
        }

    request: Dict[str, Any] = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": normalize_price(price, symbol),
        "deviation": int(deviation),
        "magic": int(MT5_MAGIC_NUMBER),
        "comment": str(MT5_ORDER_COMMENT),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": get_filling_mode(symbol),
    }

    if sl is not None:
        request["sl"] = normalize_price(sl, symbol)

    if tp is not None:
        request["tp"] = normalize_price(tp, symbol)

    try:
        result = mt5.order_check(request)

        if result is None:
            return {
                "valid": False,
                "retcode": None,
                "comment": "order_check returned None.",
                "request": request,
            }

        retcode = getattr(
            result,
            "retcode",
            None,
        )

        comment = str(
            getattr(
                result,
                "comment",
                "",
            )
        )

        # MT5 normally returns 0 for successful order_check.
        valid = (
            retcode == 0
            or retcode == mt5.TRADE_RETCODE_DONE
        )

        return {
            "valid": bool(valid),
            "retcode": retcode,
            "comment": comment,
            "request": request,
            "result": result,
        }

    except Exception as exc:
        return {
            "valid": False,
            "retcode": None,
            "comment": str(exc),
            "request": request,
        }


# ============================================================
# MARKET ORDER
# ============================================================

def send_market_order(
    symbol: str = PILOT_SYMBOL,
    side: str = "BUY",
    volume: Optional[float] = None,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    deviation: int = DEFAULT_DEVIATION,
    comment: Optional[str] = None,
    magic: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Safe market-order gateway.

    PAPER_TRADING=True or ALLOW_LIVE_TRADING=False prevents
    mt5.order_send() from ever being called.
    """

    symbol = _normalize_symbol(symbol)
    side = str(side).strip().upper()

    requested_volume = (
        volume
        if volume is not None
        else lot
        if lot is not None
        else DEFAULT_LOT
    )

    volume_value = normalize_volume(
        requested_volume,
        symbol,
    )

    # --------------------------------------------------------
    # HARD SYMBOL GATE
    # --------------------------------------------------------

    if symbol != PILOT_SYMBOL:
        return {
            "success": False,
            "blocked": True,
            "reason": (
                f"Symbol {symbol} rejected. "
                f"Pilot symbol is {PILOT_SYMBOL}."
            ),
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # SIDE GATE
    # --------------------------------------------------------

    if side not in {"BUY", "SELL"}:
        return {
            "success": False,
            "blocked": True,
            "reason": "Invalid order side.",
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # CONNECTION
    # --------------------------------------------------------

    if not ensure_connection():
        return {
            "success": False,
            "blocked": True,
            "reason": "MT5 connection unavailable.",
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # POSITION LIMIT
    # --------------------------------------------------------

    position_gate = validate_position_limit()

    if not position_gate["valid"]:
        return {
            "success": False,
            "blocked": True,
            "reason": position_gate["reason"],
            "position_gate": position_gate,
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # DUPLICATE DIRECTION
    # --------------------------------------------------------

    if has_open_direction(side, symbol):
        return {
            "success": False,
            "blocked": True,
            "reason": (
                f"Existing {side} position already "
                f"exists for {symbol}."
            ),
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # DAILY LOSS
    # --------------------------------------------------------

    daily_gate = validate_daily_loss_limit(5.0)

    if not daily_gate["valid"]:
        return {
            "success": False,
            "blocked": True,
            "reason": daily_gate["reason"],
            "daily_gate": daily_gate,
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # MARGIN
    # --------------------------------------------------------

    margin_gate = validate_margin(
        symbol=symbol,
        volume=volume_value,
        side=side,
    )

    if not margin_gate["valid"]:
        return {
            "success": False,
            "blocked": True,
            "reason": margin_gate["reason"],
            "margin_gate": margin_gate,
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    # --------------------------------------------------------
    # PAPER TRADING HARD BLOCK
    # --------------------------------------------------------

    if bool(PAPER_TRADING):
        return {
            "success": False,
            "blocked": True,
            "paper": True,
            "reason": (
                "PAPER_TRADING=True. "
                "No real order was sent."
            ),
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
            "sl": sl,
            "tp": tp,
        }

    # --------------------------------------------------------
    # LIVE SAFETY HARD BLOCK
    # --------------------------------------------------------

    if not live_trading_allowed():
        return {
            "success": False,
            "blocked": True,
            "paper": False,
            "reason": (
                "Live trading safety gate is closed. "
                "No real order was sent."
            ),
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
            "sl": sl,
            "tp": tp,
        }

    # --------------------------------------------------------
    # ORDER CHECK
    # --------------------------------------------------------

    check = order_check(
        symbol=symbol,
        side=side,
        volume=volume_value,
        sl=sl,
        tp=tp,
        deviation=deviation,
    )

    if not check.get("valid", False):
        return {
            "success": False,
            "blocked": True,
            "reason": (
                "MT5 order_check rejected the order."
            ),
            "check": check,
            "symbol": symbol,
            "side": side,
            "volume": volume_value,
        }

    request = dict(
        check["request"]
    )

    if comment:
        request["comment"] = str(comment)

    if magic is not None:
        request["magic"] = int(magic)

    # --------------------------------------------------------
    # FINAL SAFETY GATE
    # --------------------------------------------------------

    if not live_trading_allowed():
        return {
            "success": False,
            "blocked": True,
            "reason": (
                "Final live-trading gate closed "
                "immediately before order_send()."
            ),
            "request": request,
        }

    # --------------------------------------------------------
    # REAL ORDER SEND
    # --------------------------------------------------------

    try:
        result = mt5.order_send(request)

    except Exception as exc:
        return {
            "success": False,
            "blocked": False,
            "reason": f"order_send exception: {exc}",
            "request": request,
        }

    if result is None:
        return {
            "success": False,
            "blocked": False,
            "reason": "MT5 order_send returned None.",
            "request": request,
        }

    retcode = getattr(
        result,
        "retcode",
        None,
    )

    order_ticket = _safe_int(
        getattr(result, "order", 0),
        0,
    )

    deal_ticket = _safe_int(
        getattr(result, "deal", 0),
        0,
    )

    success = retcode in {
        mt5.TRADE_RETCODE_DONE,
        mt5.TRADE_RETCODE_DONE_PARTIAL,
    }

    return {
        "success": bool(success),
        "blocked": False,
        "retcode": retcode,
        "comment": str(
            getattr(
                result,
                "comment",
                "",
            )
        ),
        "order": order_ticket,
        "ticket": order_ticket,
        "deal": deal_ticket,
        "symbol": symbol,
        "side": side,
        "volume": volume_value,
        "sl": sl,
        "tp": tp,
        "request": request,
        "result": result,
    }


# ============================================================
# TRADE STATUS
# ============================================================

def update_trade_status(
    ticket: int,
) -> Optional[Any]:
    """
    Find a position/order by ticket where possible.
    """

    if not ensure_connection():
        return None

    ticket = _safe_int(ticket)

    if ticket <= 0:
        return None

    try:
        positions = mt5.positions_get(ticket=ticket)

        if positions:
            return positions[0]

    except Exception:
        pass

    try:
        orders = mt5.orders_get(ticket=ticket)

        if orders:
            return orders[0]

    except Exception:
        pass

    return None


# ============================================================
# CLASS API
# ============================================================

class MT5Connector:
    """
    Object-oriented compatibility layer.
    """

    def __init__(
        self,
        symbol: str = PILOT_SYMBOL,
    ) -> None:
        self.symbol = _normalize_symbol(symbol)

    def initialize(self) -> bool:
        return initialize_mt5()

    def shutdown(self) -> bool:
        return shutdown_mt5()

    def ensure_connection(self) -> bool:
        return ensure_connection()

    def is_connected(self) -> bool:
        return is_connected()

    def get_account_info(self) -> Optional[Any]:
        return get_account_info()

    def get_account_snapshot(self) -> Dict[str, Any]:
        return get_account_snapshot()

    def get_terminal_permissions(self) -> Dict[str, Any]:
        return get_terminal_permissions()

    def get_symbol_info(
        self,
        symbol: Optional[str] = None,
    ) -> Optional[Any]:
        return get_symbol_info(
            symbol or self.symbol
        )

    def get_symbol_tick(
        self,
        symbol: Optional[str] = None,
    ) -> Optional[Any]:
        return get_symbol_tick(
            symbol or self.symbol
        )

    def get_rates(
        self,
        symbol: Optional[str] = None,
        timeframe: int = mt5.TIMEFRAME_M15,
        count: int = 100,
    ) -> Any:
        return get_rates(
            symbol or self.symbol,
            timeframe,
            count,
        )

    def normalize_price(
        self,
        price: float,
        symbol: Optional[str] = None,
    ) -> float:
        return normalize_price(
            price,
            symbol or self.symbol,
        )

    def normalize_volume(
        self,
        volume: float,
        symbol: Optional[str] = None,
    ) -> float:
        return normalize_volume(
            volume,
            symbol or self.symbol,
        )

    def get_filling_mode(
        self,
        symbol: Optional[str] = None,
    ) -> int:
        return get_filling_mode(
            symbol or self.symbol
        )

    def get_open_positions(
        self,
        symbol: Optional[str] = None,
    ) -> List[Any]:
        return get_open_positions(
            symbol or self.symbol
            if symbol is not None
            else self.symbol
        )

    def get_project_position_count(self) -> int:
        return get_project_position_count()

    def get_daily_loss_snapshot(self) -> Dict[str, Any]:
        return get_daily_loss_snapshot()

    def get_free_margin(self) -> float:
        return get_free_margin()

    def calculate_margin(
        self,
        volume: float,
        order_type: int,
        price: Optional[float] = None,
        symbol: Optional[str] = None,
    ) -> float:
        return calculate_margin(
            symbol or self.symbol,
            volume,
            order_type,
            price,
        )

    def live_trading_allowed(self) -> bool:
        return live_trading_allowed()

    def order_check(
        self,
        side: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
    ) -> Dict[str, Any]:
        return order_check(
            symbol=self.symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
        )

    def send_market_order(
        self,
        side: str,
        volume: Optional[float] = None,
        lot: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        deviation: int = DEFAULT_DEVIATION,
        comment: Optional[str] = None,
        magic: Optional[int] = None,
    ) -> Dict[str, Any]:
        return send_market_order(
            symbol=self.symbol,
            side=side,
            volume=volume,
            lot=lot,
            sl=sl,
            tp=tp,
            deviation=deviation,
            comment=comment,
            magic=magic,
        )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Constants
    "PILOT_SYMBOL",
    "DEFAULT_SYMBOL",
    "DEFAULT_MAGIC",
    "DEFAULT_DEVIATION",
    "MT5_MAGIC_NUMBER",
    "MT5_ORDER_COMMENT",
    "MIN_PROJECT_LOT",
    "DEFAULT_LOT",
    "MAX_PROJECT_LOT",
    "MAX_OPEN_TRADES",
    "PAPER_TRADING",
    "ALLOW_LIVE_TRADING",

    # Connection
    "initialize_mt5",
    "shutdown_mt5",
    "ensure_connection",
    "is_connected",

    # Information
    "get_terminal_info",
    "get_terminal_permissions",
    "get_account_info",
    "get_account_snapshot",
    "get_free_margin",

    # Symbol
    "get_symbol_info",
    "get_symbol_tick",
    "get_rates",

    # Price / volume
    "normalize_price",
    "normalize_volume",
    "get_filling_mode",

    # Positions
    "get_open_positions",
    "get_project_positions",
    "get_project_position_count",
    "has_open_direction",

    # Risk
    "get_daily_loss_snapshot",
    "validate_daily_loss_limit",
    "validate_position_limit",
    "calculate_margin",
    "validate_margin",

    # Safety
    "live_trading_allowed",
    "trading_safety_status",

    # Orders
    "order_check",
    "send_market_order",
    "update_trade_status",

    # Class
    "MT5Connector",
]
