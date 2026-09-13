# core/mt5_connector.py
# Pourya Trader AI
# MT5 Safe Connector — XAUUSD.su / OtetGroup-MT5
#
# IMPORTANT:
# PAPER_TRADING=True and ALLOW_LIVE_TRADING=False must remain enabled
# until explicit final approval for live trading.

from __future__ import annotations

import math
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

try:
    from config import (
        MT5_LOGIN,
        MT5_PASSWORD,
        MT5_SERVER,
        MT5_TERMINAL_PATH,
        MT5_PORTABLE,
        MT5_TIMEOUT,
        PILOT_SYMBOL,
        MAX_OPEN_TRADES,
        MAX_PROJECT_POSITIONS,
        MIN_PROJECT_LOT,
        DEFAULT_LOT,
        MAX_PROJECT_LOT,
        PAPER_TRADING,
        ALLOW_LIVE_TRADING,
        MT5_MAGIC_NUMBER,
        MT5_DEVIATION,
        MT5_COMMENT,
        DAILY_LOSS_LIMIT_PCT,
    )
except Exception:
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0") or 0)
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "OtetGroup-MT5").strip()

    MT5_TERMINAL_PATH = os.getenv(
        "MT5_TERMINAL_PATH",
        r"C:\MT5-Pourya\terminal64.exe",
    )

    MT5_PORTABLE = True
    MT5_TIMEOUT = 60000

    PILOT_SYMBOL = "XAUUSD.su"

    MAX_OPEN_TRADES = 5
    MAX_PROJECT_POSITIONS = 5

    MIN_PROJECT_LOT = 0.01
    DEFAULT_LOT = 0.01
    MAX_PROJECT_LOT = 0.03

    PAPER_TRADING = True
    ALLOW_LIVE_TRADING = False

    MT5_MAGIC_NUMBER = int(
        os.getenv("MT5_MAGIC_NUMBER", "20260731") or 20260731
    )

    MT5_DEVIATION = int(
        os.getenv("MT5_DEVIATION", "20") or 20
    )

    MT5_COMMENT = os.getenv(
        "MT5_COMMENT",
        "Pourya Trader AI",
    )

    DAILY_LOSS_LIMIT_PCT = float(
        os.getenv("DAILY_LOSS_LIMIT_PCT", "5")
        or 5
    )


# Compatibility aliases
DEFAULT_SYMBOL = PILOT_SYMBOL
MT5_PATH = MT5_TERMINAL_PATH
MT5_PORTABLE_MODE = MT5_PORTABLE
MT5_CONNECTION_TIMEOUT = MT5_TIMEOUT


# ---------------------------------------------------------------------------
# INTERNAL STATE
# ---------------------------------------------------------------------------

_last_initialize_time = 0.0
_connection_attempts = 0


# ---------------------------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------------------------

def _require_mt5() -> bool:
    return mt5 is not None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _account_dict(info: Any) -> Dict[str, Any]:
    if info is None:
        return {}

    if hasattr(info, "_asdict"):
        try:
            return dict(info._asdict())
        except Exception:
            pass

    result: Dict[str, Any] = {}

    for name in (
        "login",
        "server",
        "balance",
        "equity",
        "profit",
        "credit",
        "margin",
        "margin_free",
        "margin_level",
        "trade_allowed",
        "trade_expert",
        "leverage",
        "currency",
        "name",
    ):
        try:
            result[name] = getattr(info, name)
        except Exception:
            pass

    return result


def _symbol_dict(info: Any) -> Dict[str, Any]:
    if info is None:
        return {}

    if hasattr(info, "_asdict"):
        try:
            return dict(info._asdict())
        except Exception:
            pass

    return {}


# ---------------------------------------------------------------------------
# INITIALIZATION / CONNECTION
# ---------------------------------------------------------------------------

def initialize_mt5(force: bool = False) -> bool:
    """
    Initialize the specific portable MT5 terminal.

    No trading order is sent here.
    """

    global _last_initialize_time
    global _connection_attempts

    if not _require_mt5():
        return False

    now = time.time()

    if not force and mt5.terminal_info() is not None:
        return True

    if not force and now - _last_initialize_time < 2:
        return mt5.terminal_info() is not None

    _connection_attempts += 1
    _last_initialize_time = now

    try:
        mt5.shutdown()
    except Exception:
        pass

    kwargs: Dict[str, Any] = {
        "path": MT5_TERMINAL_PATH,
        "portable": bool(MT5_PORTABLE),
        "timeout": int(MT5_TIMEOUT),
    }

    if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
        kwargs.update(
            {
                "login": int(MT5_LOGIN),
                "password": str(MT5_PASSWORD),
                "server": str(MT5_SERVER),
            }
        )

    try:
        ok = bool(mt5.initialize(**kwargs))
    except Exception:
        ok = False

    if not ok:
        return False

    # Select the target account if credentials were supplied.
    if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
        try:
            selected = mt5.login(
                int(MT5_LOGIN),
                password=str(MT5_PASSWORD),
                server=str(MT5_SERVER),
            )

            if not selected:
                # The terminal may already be logged into the correct account.
                info = mt5.account_info()
                if info is None:
                    return False

        except Exception:
            info = mt5.account_info()
            if info is None:
                return False

    return mt5.terminal_info() is not None


def ensure_connection() -> bool:
    """
    Ensure that MT5 is initialized and an account is available.
    """

    if not _require_mt5():
        return False

    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()

        if terminal is not None and account is not None:
            return True
    except Exception:
        pass

    return initialize_mt5(force=True)


def shutdown_mt5() -> bool:
    if not _require_mt5():
        return True

    try:
        mt5.shutdown()
        return True
    except Exception:
        return False


def is_connected() -> bool:
    if not _require_mt5():
        return False

    try:
        return (
            mt5.terminal_info() is not None
            and mt5.account_info() is not None
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# ACCOUNT / TERMINAL
# ---------------------------------------------------------------------------

def get_account_info() -> Optional[Dict[str, Any]]:
    if not ensure_connection():
        return None

    try:
        info = mt5.account_info()
        return _account_dict(info)
    except Exception:
        return None


def get_account_snapshot() -> Dict[str, Any]:
    info = get_account_info()

    if not info:
        return {
            "connected": False,
            "login": 0,
            "server": "",
            "balance": 0.0,
            "equity": 0.0,
            "profit": 0.0,
            "credit": 0.0,
            "margin": 0.0,
            "free_margin": 0.0,
            "margin_level": 0.0,
            "trade_allowed": False,
            "trade_expert": False,
        }

    return {
        "connected": True,
        "login": _safe_int(info.get("login")),
        "server": info.get("server", ""),
        "balance": _safe_float(info.get("balance")),
        "equity": _safe_float(info.get("equity")),
        "profit": _safe_float(info.get("profit")),
        "credit": _safe_float(info.get("credit")),
        "margin": _safe_float(info.get("margin")),
        "free_margin": _safe_float(info.get("margin_free")),
        "margin_level": _safe_float(info.get("margin_level")),
        "trade_allowed": bool(info.get("trade_allowed", False)),
        "trade_expert": bool(info.get("trade_expert", False)),
    }


def get_free_margin() -> float:
    snapshot = get_account_snapshot()
    return _safe_float(snapshot.get("free_margin"))


def get_terminal_permissions() -> Dict[str, Any]:
    if not ensure_connection():
        return {
            "connected": False,
            "trade_allowed": False,
            "trade_expert": False,
            "dlls_allowed": False,
            "email_enabled": False,
            "notifications_enabled": False,
        }

    try:
        terminal = mt5.terminal_info()

        if terminal is None:
            return {
                "connected": False,
                "trade_allowed": False,
                "trade_expert": False,
                "dlls_allowed": False,
                "email_enabled": False,
                "notifications_enabled": False,
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
            "email_enabled": bool(
                getattr(terminal, "email_enabled", False)
            ),
            "notifications_enabled": bool(
                getattr(terminal, "notifications_enabled", False)
            ),
        }

    except Exception:
        return {
            "connected": False,
            "trade_allowed": False,
            "trade_expert": False,
            "dlls_allowed": False,
            "email_enabled": False,
            "notifications_enabled": False,
        }


# ---------------------------------------------------------------------------
# SYMBOL / MARKET DATA
# ---------------------------------------------------------------------------

def get_symbol_info(
    symbol: str = PILOT_SYMBOL,
) -> Optional[Any]:
    if not ensure_connection():
        return None

    if symbol != PILOT_SYMBOL:
        return None

    try:
        info = mt5.symbol_info(symbol)

        if info is None:
            return None

        if not bool(getattr(info, "visible", True)):
            try:
                mt5.symbol_select(symbol, True)
            except Exception:
                pass

        return info

    except Exception:
        return None


def get_symbol_tick(
    symbol: str = PILOT_SYMBOL,
) -> Optional[Any]:
    if not ensure_connection():
        return None

    if symbol != PILOT_SYMBOL:
        return None

    try:
        return mt5.symbol_info_tick(symbol)
    except Exception:
        return None


def get_rates(
    symbol: str = PILOT_SYMBOL,
    timeframe: Any = None,
    count: int = 100,
    start_pos: int = 0,
) -> Any:
    if not ensure_connection():
        return None

    if symbol != PILOT_SYMBOL:
        return None

    if timeframe is None:
        timeframe = mt5.TIMEFRAME_M15

    try:
        return mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            start_pos,
            int(count),
        )
    except Exception:
        return None


def get_filling_mode(
    symbol: str = PILOT_SYMBOL,
) -> Optional[int]:
    """
    Return the broker-supported filling mode.

    Prefer RETURN when available, then IOC, then FOK.
    """

    info = get_symbol_info(symbol)

    if info is None:
        return None

    try:
        mask = int(getattr(info, "filling_mode", 0))

        # MT5 filling mode bit flags:
        # FOK = 1
        # IOC = 2
        # RETURN = 4 is not always represented in filling_mode.
        #
        # For market execution, broker behavior varies. We therefore
        # prefer the explicit supported flags and fall back safely.

        if mask & getattr(mt5, "SYMBOL_FILLING_FOK", 1):
            return mt5.ORDER_FILLING_FOK

        if mask & getattr(mt5, "SYMBOL_FILLING_IOC", 2):
            return mt5.ORDER_FILLING_IOC

        # RETURN is generally accepted where supported.
        if hasattr(mt5, "ORDER_FILLING_RETURN"):
            return mt5.ORDER_FILLING_RETURN

    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_price(
    price: float,
    symbol: str = PILOT_SYMBOL,
) -> float:
    info = get_symbol_info(symbol)

    if info is None:
        return float(price)

    digits = _safe_int(getattr(info, "digits", 2), 2)

    return round(float(price), digits)


def normalize_volume(
    volume: float,
    symbol: str = PILOT_SYMBOL,
) -> float:
    """
    Normalize project volume to broker constraints and project limits.

    Project hard range:
        0.01 <= lot <= 0.03
    """

    info = get_symbol_info(symbol)

    requested = _safe_float(volume, DEFAULT_LOT)

    lower = max(
        _safe_float(MIN_PROJECT_LOT, 0.01),
        0.0,
    )

    upper = min(
        _safe_float(MAX_PROJECT_LOT, 0.03),
        _safe_float(MAX_PROJECT_LOT, 0.03),
    )

    if info is not None:
        broker_min = _safe_float(
            getattr(info, "volume_min", lower),
            lower,
        )

        broker_max = _safe_float(
            getattr(info, "volume_max", upper),
            upper,
        )

        broker_step = _safe_float(
            getattr(info, "volume_step", 0.01),
            0.01,
        )

        lower = max(lower, broker_min)
        upper = min(upper, broker_max)

        if broker_step <= 0:
            broker_step = 0.01
    else:
        broker_step = 0.01

    requested = max(lower, min(requested, upper))

    # Floor to the broker's volume step.
    steps = math.floor(
        ((requested - lower) / broker_step) + 1e-9
    )

    normalized = lower + steps * broker_step

    normalized = max(lower, min(normalized, upper))

    # Avoid floating-point artifacts.
    decimals = 2

    if broker_step < 0.01:
        decimals = 4

    return round(normalized, decimals)


# ---------------------------------------------------------------------------
# POSITIONS
# ---------------------------------------------------------------------------

def get_open_positions(
    symbol: Optional[str] = None,
) -> List[Any]:
    if not ensure_connection():
        return []

    target = symbol or PILOT_SYMBOL

    if target != PILOT_SYMBOL:
        return []

    try:
        positions = mt5.positions_get(symbol=target)

        if positions is None:
            return []

        return list(positions)

    except Exception:
        return []


def get_project_positions() -> List[Any]:
    return get_open_positions(PILOT_SYMBOL)


def get_project_position_count() -> int:
    return len(get_project_positions())


def has_open_direction(
    side: str,
    symbol: str = PILOT_SYMBOL,
) -> bool:
    if symbol != PILOT_SYMBOL:
        return False

    normalized = str(side).strip().upper()

    positions = get_open_positions(symbol)

    for position in positions:
        position_type = getattr(position, "type", None)

        if normalized == "BUY":
            if position_type == getattr(mt5, "POSITION_TYPE_BUY", 0):
                return True

        elif normalized == "SELL":
            if position_type == getattr(mt5, "POSITION_TYPE_SELL", 1):
                return True

    return False


# ---------------------------------------------------------------------------
# RISK / DAILY LOSS
# ---------------------------------------------------------------------------

def get_daily_loss_snapshot() -> Dict[str, Any]:
    """
    Integration-safe daily loss snapshot.

    NOTE:
    This is intentionally conservative but does not yet persist a true
    midnight equity baseline. A persistent daily baseline should be added
    before production deployment.
    """

    snapshot = get_account_snapshot()

    equity = _safe_float(snapshot.get("equity"))
    balance = _safe_float(snapshot.get("balance"))
    profit = _safe_float(snapshot.get("profit"))

    # If current account equity is below balance, calculate current loss.
    loss_amount = max(0.0, balance - equity)

    reference = max(
        abs(balance),
        abs(equity),
        0.01,
    )

    loss_pct = (loss_amount / reference) * 100.0

    return {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "balance": balance,
        "equity": equity,
        "profit": profit,
        "loss_amount": loss_amount,
        "loss_pct": loss_pct,
        "limit_pct": float(DAILY_LOSS_LIMIT_PCT),
        "within_limit": loss_pct < float(DAILY_LOSS_LIMIT_PCT),
    }


def validate_daily_loss_limit() -> Dict[str, Any]:
    result = get_daily_loss_snapshot()

    return {
        "allowed": bool(result.get("within_limit", False)),
        **result,
    }


def validate_position_limit() -> Dict[str, Any]:
    count = get_project_position_count()
    limit = int(MAX_PROJECT_POSITIONS)

    return {
        "allowed": count < limit,
        "count": count,
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# MARGIN
# ---------------------------------------------------------------------------

def calculate_margin(
    side: str,
    volume: float,
    price: Optional[float] = None,
    symbol: str = PILOT_SYMBOL,
) -> Optional[float]:
    if not ensure_connection():
        return None

    if symbol != PILOT_SYMBOL:
        return None

    normalized_side = str(side).strip().upper()

    if normalized_side == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
    elif normalized_side == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return None

    lot = normalize_volume(volume, symbol)

    if price is None:
        tick = get_symbol_tick(symbol)

        if tick is None:
            return None

        if normalized_side == "BUY":
            price = float(tick.ask)
        else:
            price = float(tick.bid)

    try:
        margin = mt5.order_calc_margin(
            order_type,
            symbol,
            lot,
            float(price),
        )

        if margin is None:
            return None

        return float(margin)

    except Exception:
        return None


def validate_margin(
    side: str,
    volume: float,
    price: Optional[float] = None,
    symbol: str = PILOT_SYMBOL,
) -> Dict[str, Any]:
    required = calculate_margin(
        side,
        volume,
        price,
        symbol,
    )

    free_margin = get_free_margin()

    if required is None:
        return {
            "allowed": False,
            "required_margin": None,
            "free_margin": free_margin,
            "reason": "margin_calculation_failed",
        }

    allowed = required <= free_margin

    return {
        "allowed": allowed,
        "required_margin": required,
        "free_margin": free_margin,
        "remaining_margin": free_margin - required,
        "reason": "ok" if allowed else "insufficient_margin",
    }


# ---------------------------------------------------------------------------
# SAFETY
# ---------------------------------------------------------------------------

def live_trading_allowed() -> bool:
    """
    FINAL LIVE GATE.

    Both conditions must be true.
    Current project configuration intentionally keeps this False.
    """

    return bool(
        ALLOW_LIVE_TRADING
        and not PAPER_TRADING
    )


def trading_safety_status() -> Dict[str, Any]:
    permissions = get_terminal_permissions()
    account = get_account_snapshot()
    positions = validate_position_limit()
    daily_loss = validate_daily_loss_limit()

    live_allowed = live_trading_allowed()

    return {
        "connected": bool(account.get("connected", False)),
        "server": account.get("server", ""),
        "login": account.get("login", 0),
        "symbol": PILOT_SYMBOL,
        "trade_allowed": bool(
            permissions.get("trade_allowed", False)
        ),
        "trade_expert": bool(
            permissions.get("trade_expert", False)
        ),
        "paper_trading": bool(PAPER_TRADING),
        "allow_live_trading": bool(ALLOW_LIVE_TRADING),
        "live_trading_allowed": live_allowed,
        "position_limit_allowed": positions["allowed"],
        "position_count": positions["count"],
        "position_limit": positions["limit"],
        "daily_loss_allowed": daily_loss["allowed"],
        "daily_loss_pct": daily_loss["loss_pct"],
        "daily_loss_limit_pct": daily_loss["limit_pct"],
        "free_margin": account.get("free_margin", 0.0),
    }


# ---------------------------------------------------------------------------
# ORDER CHECK
# ---------------------------------------------------------------------------

def order_check(
    side: str,
    volume: float,
    price: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    symbol: str = PILOT_SYMBOL,
    comment: str = MT5_COMMENT,
) -> Optional[Any]:
    """
    Run MT5 order_check without sending an order.
    """

    if not ensure_connection():
        return None

    if symbol != PILOT_SYMBOL:
        return None

    normalized_side = str(side).strip().upper()

    if normalized_side == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
    elif normalized_side == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return None

    tick = get_symbol_tick(symbol)

    if tick is None:
        return None

    if price is None:
        price = float(
            tick.ask
            if normalized_side == "BUY"
            else tick.bid
        )

    lot = normalize_volume(volume, symbol)
    price = normalize_price(price, symbol)

    if sl is not None:
        sl = normalize_price(sl, symbol)

    if tp is not None:
        tp = normalize_price(tp, symbol)

    filling = get_filling_mode(symbol)

    request: Dict[str, Any] = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": int(MT5_DEVIATION),
        "magic": int(MT5_MAGIC_NUMBER),
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    if filling is not None:
        request["type_filling"] = filling

    if sl is not None:
        request["sl"] = sl

    if tp is not None:
        request["tp"] = tp

    try:
        return mt5.order_check(request)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# MARKET ORDER
# ---------------------------------------------------------------------------

def send_market_order(
    side: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    symbol: str = PILOT_SYMBOL,
    comment: str = MT5_COMMENT,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Safe market-order entry point.

    IMPORTANT:
    With PAPER_TRADING=True or ALLOW_LIVE_TRADING=False this function
    NEVER calls mt5.order_send().
    """

    normalized_side = str(side).strip().upper()

    # ------------------------------------------------------------------
    # FINAL ABSOLUTE SAFETY GATE
    # ------------------------------------------------------------------

    if not live_trading_allowed():
        return {
            "success": False,
            "live_order_sent": False,
            "paper_block": True,
            "reason": (
                "LIVE_TRADING_BLOCKED: "
                "PAPER_TRADING=True or ALLOW_LIVE_TRADING=False"
            ),
        }

    if symbol != PILOT_SYMBOL:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "symbol_not_allowed",
            "symbol": symbol,
            "pilot_symbol": PILOT_SYMBOL,
        }

    if normalized_side not in {"BUY", "SELL"}:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "invalid_side",
        }

    if confidence is not None:
        try:
            if float(confidence) < 60.0:
                return {
                    "success": False,
                    "live_order_sent": False,
                    "reason": "confidence_below_60",
                    "confidence": float(confidence),
                }
        except Exception:
            return {
                "success": False,
                "live_order_sent": False,
                "reason": "invalid_confidence",
            }

    if not ensure_connection():
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "mt5_not_connected",
        }

    permissions = get_terminal_permissions()

    if not permissions.get("trade_allowed", False):
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "terminal_trade_not_allowed",
        }

    if not permissions.get("trade_expert", False):
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "expert_trading_not_allowed",
        }

    position_gate = validate_position_limit()

    if not position_gate["allowed"]:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "max_position_limit_reached",
            "positions": position_gate["count"],
            "limit": position_gate["limit"],
        }

    if has_open_direction(normalized_side, symbol):
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "duplicate_direction_blocked",
            "side": normalized_side,
        }

    daily_gate = validate_daily_loss_limit()

    if not daily_gate["allowed"]:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "daily_loss_limit_reached",
            "daily_loss": daily_gate,
        }

    lot = normalize_volume(volume, symbol)

    tick = get_symbol_tick(symbol)

    if tick is None:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "tick_unavailable",
        }

    if normalized_side == "BUY":
        price = float(tick.ask)
    else:
        price = float(tick.bid)

    price = normalize_price(price, symbol)

    margin_gate = validate_margin(
        normalized_side,
        lot,
        price,
        symbol,
    )

    if not margin_gate["allowed"]:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": margin_gate["reason"],
            "margin": margin_gate,
        }

    check = order_check(
        normalized_side,
        lot,
        price,
        sl,
        tp,
        symbol,
        comment,
    )

    if check is None:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "order_check_failed_or_unavailable",
        }

    check_retcode = _safe_int(
        getattr(check, "retcode", -1),
        -1,
    )

    valid_check_codes = {
        0,
        getattr(mt5, "TRADE_RETCODE_DONE", 10009),
    }

    if check_retcode not in valid_check_codes:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "order_check_rejected",
            "retcode": check_retcode,
            "check": (
                check._asdict()
                if hasattr(check, "_asdict")
                else str(check)
            ),
        }

    # ------------------------------------------------------------------
    # SECOND / FINAL LIVE GATE
    # ------------------------------------------------------------------

    if not live_trading_allowed():
        return {
            "success": False,
            "live_order_sent": False,
            "paper_block": True,
            "reason": "live_gate_closed_before_order_send",
        }

    if normalized_side == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
    else:
        order_type = mt5.ORDER_TYPE_SELL

    request: Dict[str, Any] = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": int(MT5_DEVIATION),
        "magic": int(MT5_MAGIC_NUMBER),
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    if sl is not None:
        request["sl"] = normalize_price(sl, symbol)

    if tp is not None:
        request["tp"] = normalize_price(tp, symbol)

    filling = get_filling_mode(symbol)

    if filling is not None:
        request["type_filling"] = filling

    try:
        result = mt5.order_send(request)
    except Exception as exc:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "order_send_exception",
            "error": str(exc),
        }

    if result is None:
        return {
            "success": False,
            "live_order_sent": False,
            "reason": "order_send_returned_none",
        }

    retcode = _safe_int(
        getattr(result, "retcode", -1),
        -1,
    )

    success_codes = {
        getattr(mt5, "TRADE_RETCODE_DONE", 10009),
        getattr(mt5, "TRADE_RETCODE_PLACED", 10008),
    }

    success = retcode in success_codes

    return {
        "success": success,
        "live_order_sent": True,
        "retcode": retcode,
        "order": getattr(result, "order", 0),
        "deal": getattr(result, "deal", 0),
        "volume": lot,
        "price": price,
        "symbol": symbol,
        "side": normalized_side,
        "result": (
            result._asdict()
            if hasattr(result, "_asdict")
            else str(result)
        ),
    }


# ---------------------------------------------------------------------------
# TRADE STATUS
# ---------------------------------------------------------------------------

def update_trade_status(
    ticket: int,
) -> Dict[str, Any]:
    if not ensure_connection():
        return {
            "found": False,
            "ticket": int(ticket),
            "reason": "not_connected",
        }

    ticket = int(ticket)

    try:
        positions = mt5.positions_get(ticket=ticket)

        if positions:
            position = positions[0]

            return {
                "found": True,
                "open": True,
                "ticket": ticket,
                "symbol": getattr(position, "symbol", ""),
                "volume": getattr(position, "volume", 0.0),
                "type": getattr(position, "type", None),
                "price_open": getattr(position, "price_open", 0.0),
                "sl": getattr(position, "sl", 0.0),
                "tp": getattr(position, "tp", 0.0),
                "profit": getattr(position, "profit", 0.0),
            }

        return {
            "found": False,
            "open": False,
            "ticket": ticket,
        }

    except Exception as exc:
        return {
            "found": False,
            "open": False,
            "ticket": ticket,
            "reason": str(exc),
        }


# ---------------------------------------------------------------------------
# CONNECTOR CLASS
# ---------------------------------------------------------------------------

class MT5Connector:
    """
    Compatibility wrapper around the functional connector API.
    """

    PILOT_SYMBOL = PILOT_SYMBOL

    def __init__(
        self,
        symbol: str = PILOT_SYMBOL,
    ) -> None:
        self.symbol = symbol

    def initialize(self) -> bool:
        return initialize_mt5()

    def ensure_connection(self) -> bool:
        return ensure_connection()

    def shutdown(self) -> bool:
        return shutdown_mt5()

    def is_connected(self) -> bool:
        return is_connected()

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        return get_account_info()

    def get_account_snapshot(self) -> Dict[str, Any]:
        return get_account_snapshot()

    def get_terminal_permissions(self) -> Dict[str, Any]:
        return get_terminal_permissions()

    def get_symbol_info(self) -> Optional[Any]:
        return get_symbol_info(self.symbol)

    def get_symbol_tick(self) -> Optional[Any]:
        return get_symbol_tick(self.symbol)

    def get_rates(
        self,
        timeframe: Any = None,
        count: int = 100,
        start_pos: int = 0,
    ) -> Any:
        return get_rates(
            self.symbol,
            timeframe,
            count,
            start_pos,
        )

    def normalize_price(self, price: float) -> float:
        return normalize_price(price, self.symbol)

    def normalize_volume(self, volume: float) -> float:
        return normalize_volume(volume, self.symbol)

    def get_open_positions(self) -> List[Any]:
        return get_open_positions(self.symbol)

    def send_market_order(
        self,
        side: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = MT5_COMMENT,
        confidence: Optional[float] = None,
    ) -> Dict[str, Any]:
        return send_market_order(
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            symbol=self.symbol,
            comment=comment,
            confidence=confidence,
        )

    def trading_safety_status(self) -> Dict[str, Any]:
        return trading_safety_status()


# ---------------------------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "PILOT_SYMBOL",
    "DEFAULT_SYMBOL",

    "MT5Connector",

    "initialize_mt5",
    "ensure_connection",
    "shutdown_mt5",
    "is_connected",

    "get_account_info",
    "get_account_snapshot",
    "get_free_margin",
    "get_terminal_permissions",

    "get_symbol_info",
    "get_symbol_tick",
    "get_filling_mode",
    "get_rates",

    "normalize_price",
    "normalize_volume",

    "get_open_positions",
    "get_project_positions",
    "get_project_position_count",
    "has_open_direction",

    "get_daily_loss_snapshot",
    "validate_daily_loss_limit",
    "validate_position_limit",

    "calculate_margin",
    "validate_margin",

    "live_trading_allowed",
    "trading_safety_status",

    "order_check",
    "send_market_order",

    "update_trade_status",
]
