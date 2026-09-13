# core/mt5_connector.py

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence

import MetaTrader5 as mt5

from config import (
    ALLOW_LIVE_TRADING,
    DEFAULT_LOT,
    MAX_DAILY_LOSS_PERCENT,
    MAX_OPEN_TRADES,
    MAX_PROJECT_LOT,
    MIN_PROJECT_LOT,
    MT5_DEVIATION,
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


# ============================================================
# PROJECT CONSTANTS
# ============================================================

PILOT_SYMBOL = PILOT_SYMBOL

DEFAULT_SYMBOL = PILOT_SYMBOL
DEFAULT_MAGIC = MT5_MAGIC_NUMBER
DEFAULT_DEVIATION = MT5_DEVIATION
DEFAULT_COMMENT = MT5_ORDER_COMMENT

PROJECT_MIN_LOT = float(MIN_PROJECT_LOT)
PROJECT_MAX_LOT = float(MAX_PROJECT_LOT)
PROJECT_MAX_POSITIONS = min(max(int(MAX_OPEN_TRADES), 1), 5)

MT5_TIMEOUT_MS = int(MT5_TIMEOUT)


# ============================================================
# LOGGING
# ============================================================

try:
    from core.logger import logger
except Exception:
    import logging

    logger = logging.getLogger("pourya_mt5_connector")


# ============================================================
# INTERNAL HELPERS
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


def _retcode_name(retcode: Any) -> str:
    try:
        return str(mt5.TRADE_RETCODE(retcode))
    except Exception:
        return str(retcode)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _today_utc_range() -> tuple[datetime, datetime]:
    now = _utc_now()

    start = datetime(
        now.year,
        now.month,
        now.day,
        tzinfo=timezone.utc,
    )

    end = start + timedelta(days=1)

    return start, end


def _is_project_position(position: Any) -> bool:
    if position is None:
        return False

    symbol = str(getattr(position, "symbol", "") or "")

    magic = _safe_int(
        getattr(position, "magic", 0),
        0,
    )

    return (
        symbol == PILOT_SYMBOL
        and magic == DEFAULT_MAGIC
    )


# ============================================================
# SAFETY GATE
# ============================================================

def live_trading_allowed() -> bool:
    """
    Final fail-closed gate.

    Real trading is allowed ONLY when:
        PAPER_TRADING == False
        AND
        ALLOW_LIVE_TRADING == True

    Any other combination returns False.
    """

    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    return True


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_mt5(
    *,
    login: Optional[int] = None,
    password: Optional[str] = None,
    server: Optional[str] = None,
    path: Optional[str] = None,
    portable: Optional[bool] = None,
    timeout: Optional[int] = None,
) -> bool:
    """
    Initialize the exact portable MT5 terminal used by the project.

    No order is sent here.
    """

    target_login = _safe_int(
        MT5_LOGIN if login is None else login,
        0,
    )

    target_password = (
        MT5_PASSWORD
        if password is None
        else str(password)
    )

    target_server = (
        MT5_SERVER
        if server is None
        else str(server).strip()
    )

    target_path = (
        MT5_TERMINAL_PATH
        if path is None
        else str(path)
    )

    target_portable = (
        MT5_PORTABLE
        if portable is None
        else bool(portable)
    )

    target_timeout = (
        MT5_TIMEOUT_MS
        if timeout is None
        else int(timeout)
    )

    try:
        if mt5.terminal_info() is not None:
            info = mt5.account_info()

            if info is not None:
                current_login = _safe_int(
                    getattr(info, "login", 0),
                    0,
                )

                current_server = str(
                    getattr(info, "server", "") or ""
                ).strip()

                if (
                    target_login == 0
                    or (
                        current_login == target_login
                        and (
                            not target_server
                            or current_server == target_server
                        )
                    )
                ):
                    return True

        # Clean previous Python-side MT5 connection.
        try:
            mt5.shutdown()
        except Exception:
            pass

        kwargs: Dict[str, Any] = {
            "path": target_path,
            "portable": target_portable,
            "timeout": target_timeout,
        }

        if target_login:
            kwargs["login"] = target_login

        if target_password:
            kwargs["password"] = target_password

        if target_server:
            kwargs["server"] = target_server

        ok = bool(mt5.initialize(**kwargs))

        if not ok:
            logger.error(
                "MT5 INITIALIZATION FAILED | error=%s",
                mt5.last_error(),
            )
            return False

        account = mt5.account_info()

        if account is None:
            logger.error(
                "MT5 INITIALIZATION FAILED | account_info=None"
            )
            return False

        actual_login = _safe_int(
            getattr(account, "login", 0),
            0,
        )

        actual_server = str(
            getattr(account, "server", "") or ""
        ).strip()

        if target_login and actual_login != target_login:
            logger.error(
                "MT5 ACCOUNT MISMATCH | expected_login=%s actual_login=%s",
                target_login,
                actual_login,
            )
            return False

        if target_server and actual_server != target_server:
            logger.error(
                "MT5 SERVER MISMATCH | expected=%s actual=%s",
                target_server,
                actual_server,
            )
            return False

        logger.info(
            "MT5 CONNECTED | login=%s server=%s symbol=%s",
            actual_login,
            actual_server,
            PILOT_SYMBOL,
        )

        return True

    except Exception as exc:
        logger.exception(
            "MT5 INITIALIZATION EXCEPTION | %s",
            exc,
        )
        return False


def shutdown_mt5() -> None:
    try:
        mt5.shutdown()
    except Exception:
        pass


def is_connected() -> bool:
    try:
        terminal = mt5.terminal_info()
        account = mt5.account_info()

        return (
            terminal is not None
            and account is not None
        )

    except Exception:
        return False


def ensure_connection() -> bool:
    """
    Verify connection.

    If disconnected, initialize once.

    No repeated order-send retry exists here.
    """

    if is_connected():
        return True

    return initialize_mt5()


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info() -> Any:
    if not ensure_connection():
        return None

    try:
        return mt5.account_info()
    except Exception:
        return None


def get_account_snapshot() -> Dict[str, Any]:
    account = get_account_info()

    if account is None:
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
            "leverage": 0,
            "trade_allowed": False,
            "trade_expert": False,
        }

    return {
        "connected": True,
        "login": _safe_int(
            getattr(account, "login", 0),
            0,
        ),
        "server": str(
            getattr(account, "server", "") or ""
        ),
        "balance": _safe_float(
            getattr(account, "balance", 0.0)
        ),
        "equity": _safe_float(
            getattr(account, "equity", 0.0)
        ),
        "profit": _safe_float(
            getattr(account, "profit", 0.0)
        ),
        "credit": _safe_float(
            getattr(account, "credit", 0.0)
        ),
        "margin": _safe_float(
            getattr(account, "margin", 0.0)
        ),
        "free_margin": _safe_float(
            getattr(account, "margin_free", 0.0)
        ),
        "margin_level": _safe_float(
            getattr(account, "margin_level", 0.0)
        ),
        "leverage": _safe_int(
            getattr(account, "leverage", 0),
            0,
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
# TERMINAL PERMISSIONS
# ============================================================

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
        account = mt5.account_info()

        if terminal is None or account is None:
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
                getattr(
                    terminal,
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
            "dlls_allowed": bool(
                getattr(
                    terminal,
                    "dlls_allowed",
                    False,
                )
            ),
            "email_enabled": bool(
                getattr(
                    terminal,
                    "email_enabled",
                    False,
                )
            ),
            "notifications_enabled": bool(
                getattr(
                    terminal,
                    "notifications_enabled",
                    False,
                )
            ),
        }

    except Exception as exc:
        logger.exception(
            "GET TERMINAL PERMISSIONS ERROR | %s",
            exc,
        )

        return {
            "connected": False,
            "trade_allowed": False,
            "trade_expert": False,
            "dlls_allowed": False,
            "email_enabled": False,
            "notifications_enabled": False,
        }


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol: str = PILOT_SYMBOL,
) -> Any:
    if not ensure_connection():
        return None

    try:
        info = mt5.symbol_info(symbol)

        if info is None:
            return None

        if not bool(
            getattr(info, "visible", True)
        ):
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
) -> Any:
    if not ensure_connection():
        return None

    try:
        return mt5.symbol_info_tick(symbol)
    except Exception:
        return None


def get_tick(
    symbol: str = PILOT_SYMBOL,
) -> Any:
    return get_symbol_tick(symbol)


def get_filling_mode(
    symbol: str = PILOT_SYMBOL,
) -> int:
    """
    Return broker-supported filling mode.

    Prefer RETURN where supported, then IOC,
    then FOK.
    """

    info = get_symbol_info(symbol)

    if info is None:
        return mt5.ORDER_FILLING_RETURN

    supported = _safe_int(
        getattr(info, "filling_mode", 0),
        0,
    )

    # MetaTrader filling-mode flags:
    # FOK = 1
    # IOC = 2
    # RETURN is generally accepted for market/exchange modes
    # where broker permits it.

    if supported & 2:
        return mt5.ORDER_FILLING_IOC

    if supported & 1:
        return mt5.ORDER_FILLING_FOK

    return mt5.ORDER_FILLING_RETURN


# ============================================================
# TIMEFRAME / MARKET DATA
# ============================================================

def _get_timeframe(timeframe: Any) -> Any:
    if isinstance(timeframe, int):
        mapping = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            60: mt5.TIMEFRAME_H1,
            240: mt5.TIMEFRAME_H4,
            1440: mt5.TIMEFRAME_D1,
        }

        return mapping.get(
            timeframe,
            mt5.TIMEFRAME_M15,
        )

    value = str(
        timeframe or "M15"
    ).strip().upper()

    mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }

    return mapping.get(
        value,
        mt5.TIMEFRAME_M15,
    )


def get_rates(
    symbol: str = PILOT_SYMBOL,
    timeframe: Any = "M15",
    count: int = 200,
) -> Any:
    if not ensure_connection():
        return None

    try:
        return mt5.copy_rates_from_pos(
            symbol,
            _get_timeframe(timeframe),
            0,
            max(1, int(count)),
        )
    except Exception:
        return None


# ============================================================
# PRICE / VOLUME
# ============================================================

def normalize_price(
    symbol: str,
    price: float,
) -> float:
    info = get_symbol_info(symbol)

    value = _safe_float(price)

    if info is None:
        return value

    digits = _safe_int(
        getattr(info, "digits", 2),
        2,
    )

    return round(
        value,
        digits,
    )


def normalize_volume(
    volume: float,
    symbol: str = PILOT_SYMBOL,
) -> float:
    """
    Normalize project volume.

    Compatibility:
        normalize_volume(0.01)
        normalize_volume(0.01, "XAUUSD.su")
    """

    requested = _safe_float(
        volume,
        DEFAULT_LOT,
    )

    if requested <= 0:
        requested = float(DEFAULT_LOT)

    # Project hard safety ceiling.
    requested = min(
        requested,
        PROJECT_MAX_LOT,
    )

    info = get_symbol_info(symbol)

    broker_min = PROJECT_MIN_LOT
    broker_max = PROJECT_MAX_LOT
    broker_step = 0.01

    if info is not None:
        broker_min = max(
            broker_min,
            _safe_float(
                getattr(info, "volume_min", PROJECT_MIN_LOT),
                PROJECT_MIN_LOT,
            ),
        )

        broker_max = min(
            PROJECT_MAX_LOT,
            _safe_float(
                getattr(info, "volume_max", PROJECT_MAX_LOT),
                PROJECT_MAX_LOT,
            ),
        )

        broker_step = _safe_float(
            getattr(info, "volume_step", 0.01),
            0.01,
        )

        if broker_step <= 0:
            broker_step = 0.01

    requested = max(
        broker_min,
        min(requested, broker_max),
    )

    steps = math.floor(
        (requested - broker_min) / broker_step + 1e-9
    )

    normalized = (
        broker_min
        + steps * broker_step
    )

    normalized = max(
        broker_min,
        min(normalized, broker_max),
    )

    normalized = max(
        PROJECT_MIN_LOT,
        min(normalized, PROJECT_MAX_LOT),
    )

    return round(
        normalized,
        8,
    )


# ============================================================
# STOP / SL / TP VALIDATION
# ============================================================

def _minimum_stop_distance(
    symbol: str,
) -> float:
    info = get_symbol_info(symbol)

    if info is None:
        return 0.0

    point = _safe_float(
        getattr(info, "point", 0.0),
        0.0,
    )

    stops_level = _safe_int(
        getattr(info, "trade_stops_level", 0),
        0,
    )

    freeze_level = _safe_int(
        getattr(info, "trade_freeze_level", 0),
        0,
    )

    level = max(
        stops_level,
        freeze_level,
    )

    return point * level


def validate_stop_distance(
    symbol: str,
    side: str,
    entry: float,
    sl: float,
    tp: float,
) -> Dict[str, Any]:
    normalized_side = str(
        side or ""
    ).strip().upper()

    entry_value = _safe_float(entry)
    sl_value = _safe_float(sl)
    tp_value = _safe_float(tp)

    if entry_value <= 0:
        return {
            "valid": False,
            "reason": "INVALID_ENTRY",
        }

    if normalized_side not in {"BUY", "SELL"}:
        return {
            "valid": False,
            "reason": "INVALID_SIDE",
        }

    if normalized_side == "BUY":
        if sl_value <= 0 or sl_value >= entry_value:
            return {
                "valid": False,
                "reason": "BUY_SL_INVALID",
            }

        if tp_value <= entry_value:
            return {
                "valid": False,
                "reason": "BUY_TP_INVALID",
            }

    else:
        if sl_value <= 0 or sl_value <= entry_value:
            return {
                "valid": False,
                "reason": "SELL_SL_INVALID",
            }

        if tp_value <= 0 or tp_value >= entry_value:
            return {
                "valid": False,
                "reason": "SELL_TP_INVALID",
            }

    minimum_distance = _minimum_stop_distance(
        symbol
    )

    if minimum_distance > 0:
        sl_distance = abs(
            entry_value - sl_value
        )

        tp_distance = abs(
            tp_value - entry_value
        )

        if sl_distance < minimum_distance:
            return {
                "valid": False,
                "reason": "SL_TOO_CLOSE",
                "minimum_distance": minimum_distance,
                "actual_distance": sl_distance,
            }

        if tp_distance < minimum_distance:
            return {
                "valid": False,
                "reason": "TP_TOO_CLOSE",
                "minimum_distance": minimum_distance,
                "actual_distance": tp_distance,
            }

    return {
        "valid": True,
        "reason": "OK",
        "minimum_distance": minimum_distance,
    }


# ============================================================
# POSITIONS
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None,
) -> List[Any]:
    if not ensure_connection():
        return []

    try:
        if symbol:
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


def get_project_positions() -> List[Any]:
    positions = get_open_positions()

    return [
        position
        for position in positions
        if _is_project_position(position)
    ]


def get_project_position_count() -> int:
    return len(
        get_project_positions()
    )


def get_open_position_count(
    symbol: Optional[str] = None,
) -> int:
    if symbol is None:
        return get_project_position_count()

    return len([
        position
        for position in get_project_positions()
        if str(
            getattr(position, "symbol", "")
        ) == symbol
    ])


def validate_position_limit(
    max_positions: Optional[int] = None,
) -> Dict[str, Any]:
    limit = (
        PROJECT_MAX_POSITIONS
        if max_positions is None
        else min(
            max(int(max_positions), 1),
            5,
        )
    )

    count = get_project_position_count()

    return {
        "valid": count < limit,
        "current": count,
        "maximum": limit,
        "reason": (
            "OK"
            if count < limit
            else "MAX_PROJECT_POSITIONS_REACHED"
        ),
    }


# ============================================================
# DAILY LOSS
# ============================================================

def get_today_realized_profit() -> float:
    if not ensure_connection():
        return 0.0

    try:
        start, end = _today_utc_range()

        deals = mt5.history_deals_get(
            start,
            end,
        )

        if deals is None:
            return 0.0

        total = 0.0

        for deal in deals:
            symbol = str(
                getattr(
                    deal,
                    "symbol",
                    "",
                ) or ""
            )

            magic = _safe_int(
                getattr(
                    deal,
                    "magic",
                    0,
                ),
                0,
            )

            if (
                symbol != PILOT_SYMBOL
                or magic != DEFAULT_MAGIC
            ):
                continue

            total += _safe_float(
                getattr(
                    deal,
                    "profit",
                    0.0,
                )
            )

            total += _safe_float(
                getattr(
                    deal,
                    "swap",
                    0.0,
                )
            )

            total += _safe_float(
                getattr(
                    deal,
                    "commission",
                    0.0,
                )
            )

        return total

    except Exception as exc:
        logger.exception(
            "GET TODAY REALIZED PROFIT ERROR | %s",
            exc,
        )
        return 0.0


def get_daily_loss_snapshot() -> Dict[str, Any]:
    account = get_account_snapshot()

    equity = _safe_float(
        account.get("equity", 0.0)
    )

    realized_profit = get_today_realized_profit()

    # Risk is based on the actual current account equity,
    # never on INITIAL_BALANCE.
    reference_equity = max(
        equity,
        0.0,
    )

    if reference_equity > 0:
        loss_percent = max(
            0.0,
            (-realized_profit / reference_equity) * 100.0,
        )
    else:
        loss_percent = 100.0

    limit_percent = float(
        MAX_DAILY_LOSS_PERCENT
    )

    allowed = (
        loss_percent < limit_percent
    )

    return {
        "connected": bool(
            account.get("connected", False)
        ),
        "symbol": PILOT_SYMBOL,
        "magic": DEFAULT_MAGIC,
        "equity": equity,
        "realized_profit": realized_profit,
        "daily_loss_percent": loss_percent,
        "max_daily_loss_percent": limit_percent,
        "allowed": allowed,
        "reason": (
            "OK"
            if allowed
            else "MAX_DAILY_LOSS_REACHED"
        ),
    }


def validate_daily_loss_limit() -> Dict[str, Any]:
    snapshot = get_daily_loss_snapshot()

    return {
        "valid": bool(
            snapshot.get("allowed", False)
        ),
        "current_loss_percent": _safe_float(
            snapshot.get(
                "daily_loss_percent",
                100.0,
            )
        ),
        "maximum_loss_percent": _safe_float(
            snapshot.get(
                "max_daily_loss_percent",
                MAX_DAILY_LOSS_PERCENT,
            )
        ),
        "reason": snapshot.get(
            "reason",
            "UNKNOWN",
        ),
    }


# ============================================================
# MARGIN
# ============================================================

def calculate_margin(
    symbol: str,
    order_type: Any,
    volume: float,
    price: float,
) -> float:
    if not ensure_connection():
        return 0.0

    try:
        normalized_volume = normalize_volume(
            volume,
            symbol,
        )

        return _safe_float(
            mt5.order_calc_margin(
                order_type,
                symbol,
                normalized_volume,
                price,
            ),
            0.0,
        )

    except Exception:
        return 0.0


def validate_margin(
    symbol: str,
    order_type: Any,
    volume: float,
    price: float,
) -> Dict[str, Any]:
    required_margin = calculate_margin(
        symbol,
        order_type,
        volume,
        price,
    )

    free_margin = get_free_margin()

    if required_margin <= 0:
        return {
            "valid": False,
            "required_margin": required_margin,
            "free_margin": free_margin,
            "reason": "MARGIN_CALCULATION_FAILED",
        }

    # Keep a safety buffer.
    required_with_buffer = required_margin * 1.10

    valid = (
        free_margin >= required_with_buffer
    )

    return {
        "valid": valid,
        "required_margin": required_margin,
        "required_with_buffer": required_with_buffer,
        "free_margin": free_margin,
        "reason": (
            "OK"
            if valid
            else "INSUFFICIENT_FREE_MARGIN"
        ),
    }


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_symbol(
    symbol: str = PILOT_SYMBOL,
) -> Dict[str, Any]:
    if symbol != PILOT_SYMBOL:
        return {
            "valid": False,
            "reason": "PROJECT_SYMBOL_MISMATCH",
            "expected": PILOT_SYMBOL,
            "received": symbol,
        }

    info = get_symbol_info(symbol)

    if info is None:
        return {
            "valid": False,
            "reason": "SYMBOL_NOT_FOUND",
            "symbol": symbol,
        }

    return {
        "valid": True,
        "reason": "OK",
        "symbol": symbol,
        "trade_mode": _safe_int(
            getattr(info, "trade_mode", 0),
            0,
        ),
        "volume_min": _safe_float(
            getattr(info, "volume_min", 0.0),
            0.0,
        ),
        "volume_step": _safe_float(
            getattr(info, "volume_step", 0.0),
            0.0,
        ),
    }


def validate_volume(
    volume: float,
    symbol: str = PILOT_SYMBOL,
) -> Dict[str, Any]:
    normalized = normalize_volume(
        volume,
        symbol,
    )

    requested = _safe_float(
        volume,
        0.0,
    )

    valid = (
        requested > 0
        and normalized > 0
        and normalized <= PROJECT_MAX_LOT
    )

    return {
        "valid": valid,
        "requested": requested,
        "normalized": normalized,
        "minimum": PROJECT_MIN_LOT,
        "maximum": PROJECT_MAX_LOT,
        "reason": (
            "OK"
            if valid
            else "INVALID_PROJECT_VOLUME"
        ),
    }


# ============================================================
# ORDER REQUEST
# ============================================================

def _side_to_order_type(
    side: str,
) -> Optional[int]:
    normalized = str(
        side or ""
    ).strip().upper()

    if normalized == "BUY":
        return mt5.ORDER_TYPE_BUY

    if normalized == "SELL":
        return mt5.ORDER_TYPE_SELL

    return None


def _build_order_request(
    symbol: str,
    side: str,
    volume: float,
    price: float,
    sl: float,
    tp: float,
    deviation: int,
    magic: int,
    comment: str,
) -> Optional[Dict[str, Any]]:
    order_type = _side_to_order_type(
        side
    )

    if order_type is None:
        return None

    normalized_volume = normalize_volume(
        volume,
        symbol,
    )

    normalized_price = normalize_price(
        symbol,
        price,
    )

    normalized_sl = normalize_price(
        symbol,
        sl,
    )

    normalized_tp = normalize_price(
        symbol,
        tp,
    )

    return {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": normalized_volume,
        "type": order_type,
        "price": normalized_price,
        "sl": normalized_sl,
        "tp": normalized_tp,
        "deviation": int(deviation),
        "magic": int(magic),
        "comment": str(comment),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": get_filling_mode(symbol),
    }


# ============================================================
# FINAL SAFETY GATE
# ============================================================

def _final_order_safety_gate(
    symbol: str,
    side: str,
    volume: float,
    price: float,
    sl: float,
    tp: float,
) -> Dict[str, Any]:
    if not ensure_connection():
        return {
            "allowed": False,
            "reason": "MT5_NOT_CONNECTED",
        }

    if symbol != PILOT_SYMBOL:
        return {
            "allowed": False,
            "reason": "SYMBOL_NOT_ALLOWED",
        }

    if not live_trading_allowed():
        return {
            "allowed": False,
            "reason": "LIVE_TRADING_DISABLED",
        }

    account = get_account_info()

    if account is None:
        return {
            "allowed": False,
            "reason": "ACCOUNT_UNAVAILABLE",
        }

    if not bool(
        getattr(
            account,
            "trade_allowed",
            False,
        )
    ):
        return {
            "allowed": False,
            "reason": "ACCOUNT_TRADING_NOT_ALLOWED",
        }

    if not bool(
        getattr(
            account,
            "trade_expert",
            False,
        )
    ):
        return {
            "allowed": False,
            "reason": "EXPERT_TRADING_NOT_ALLOWED",
        }

    position_check = validate_position_limit()

    if not position_check["valid"]:
        return {
            "allowed": False,
            "reason": position_check["reason"],
        }

    daily_check = validate_daily_loss_limit()

    if not daily_check["valid"]:
        return {
            "allowed": False,
            "reason": daily_check["reason"],
        }

    symbol_check = validate_symbol(
        symbol
    )

    if not symbol_check["valid"]:
        return {
            "allowed": False,
            "reason": symbol_check["reason"],
        }

    volume_check = validate_volume(
        volume,
        symbol,
    )

    if not volume_check["valid"]:
        return {
            "allowed": False,
            "reason": volume_check["reason"],
        }

    stop_check = validate_stop_distance(
        symbol,
        side,
        price,
        sl,
        tp,
    )

    if not stop_check["valid"]:
        return {
            "allowed": False,
            "reason": stop_check["reason"],
        }

    order_type = _side_to_order_type(
        side
    )

    if order_type is None:
        return {
            "allowed": False,
            "reason": "INVALID_SIDE",
        }

    margin_check = validate_margin(
        symbol,
        order_type,
        volume,
        price,
    )

    if not margin_check["valid"]:
        return {
            "allowed": False,
            "reason": margin_check["reason"],
        }

    return {
        "allowed": True,
        "reason": "OK",
    }


# ============================================================
# MARKET ORDER
# ============================================================

def send_market_order(
    symbol: str = PILOT_SYMBOL,
    side: str = "",
    volume: Optional[float] = None,
    price: Optional[float] = None,
    sl: float = 0.0,
    tp: float = 0.0,
    deviation: int = DEFAULT_DEVIATION,
    magic: int = DEFAULT_MAGIC,
    comment: str = DEFAULT_COMMENT,
    lot: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Send ONE market order.

    IMPORTANT:
    This function is fail-closed.

    With:
        PAPER_TRADING=True
        ALLOW_LIVE_TRADING=False

    it will NEVER call mt5.order_send().
    """

    # Compatibility between `volume=` and old `lot=`.
    if volume is None:
        volume = lot

    if volume is None:
        volume = DEFAULT_LOT

    requested_volume = _safe_float(
        volume,
        DEFAULT_LOT,
    )

    # --------------------------------------------------------
    # HARD PAPER-TRADING BLOCK
    # --------------------------------------------------------

    if bool(PAPER_TRADING):
        return {
            "success": False,
            "sent": False,
            "paper": True,
            "live": False,
            "blocked": True,
            "reason": "PAPER_TRADING_ENABLED",
            "symbol": symbol,
            "side": side,
            "volume": requested_volume,
            "ticket": None,
            "order": None,
            "deal": None,
        }

    # --------------------------------------------------------
    # HARD LIVE FLAG BLOCK
    # --------------------------------------------------------

    if not bool(ALLOW_LIVE_TRADING):
        return {
            "success": False,
            "sent": False,
            "paper": False,
            "live": False,
            "blocked": True,
            "reason": "ALLOW_LIVE_TRADING_FALSE",
            "symbol": symbol,
            "side": side,
            "volume": requested_volume,
            "ticket": None,
            "order": None,
            "deal": None,
        }

    # --------------------------------------------------------
    # FINAL SAFETY GATE
    # --------------------------------------------------------

    if price is None:
        tick = get_symbol_tick(symbol)

        if tick is None:
            return {
                "success": False,
                "sent": False,
                "reason": "TICK_UNAVAILABLE",
                "ticket": None,
                "order": None,
                "deal": None,
            }

        if str(side).strip().upper() == "BUY":
            price = _safe_float(
                getattr(tick, "ask", 0.0)
            )
        else:
            price = _safe_float(
                getattr(tick, "bid", 0.0)
            )

    price_value = _safe_float(price)

    safety = _final_order_safety_gate(
        symbol=symbol,
        side=side,
        volume=requested_volume,
        price=price_value,
        sl=sl,
        tp=tp,
    )

    if not safety["allowed"]:
        return {
            "success": False,
            "sent": False,
            "paper": False,
            "live": False,
            "blocked": True,
            "reason": safety["reason"],
            "symbol": symbol,
            "side": side,
            "volume": requested_volume,
            "ticket": None,
            "order": None,
            "deal": None,
        }

    request = _build_order_request(
        symbol=symbol,
        side=side,
        volume=requested_volume,
        price=price_value,
        sl=sl,
        tp=tp,
        deviation=deviation,
        magic=magic,
        comment=comment,
    )

    if request is None:
        return {
            "success": False,
            "sent": False,
            "reason": "ORDER_REQUEST_BUILD_FAILED",
            "ticket": None,
            "order": None,
            "deal": None,
        }

    # --------------------------------------------------------
    # PRE-FLIGHT CHECK
    # --------------------------------------------------------

    try:
        check = mt5.order_check(
            request
        )
    except Exception as exc:
        logger.exception(
            "MT5 ORDER_CHECK EXCEPTION | %s",
            exc,
        )

        return {
            "success": False,
            "sent": False,
            "reason": "ORDER_CHECK_EXCEPTION",
            "error": str(exc),
            "ticket": None,
            "order": None,
            "deal": None,
        }

    if check is None:
        return {
            "success": False,
            "sent": False,
            "reason": "ORDER_CHECK_RETURNED_NONE",
            "ticket": None,
            "order": None,
            "deal": None,
        }

    check_retcode = _safe_int(
        getattr(check, "retcode", -1),
        -1,
    )

    # 0 is the expected success code for order_check.
    if check_retcode not in {
        0,
        getattr(
            mt5,
            "TRADE_RETCODE_DONE",
            10009,
        ),
    }:
        return {
            "success": False,
            "sent": False,
            "reason": "ORDER_CHECK_REJECTED",
            "check_retcode": check_retcode,
            "check_retcode_name": _retcode_name(
                check_retcode
            ),
            "ticket": None,
            "order": None,
            "deal": None,
        }

    # --------------------------------------------------------
    # FINAL LIVE ORDER SEND
    # --------------------------------------------------------

    try:
        result = mt5.order_send(
            request
        )
    except Exception as exc:
        logger.exception(
            "MT5 ORDER_SEND EXCEPTION | %s",
            exc,
        )

        return {
            "success": False,
            "sent": False,
            "reason": "ORDER_SEND_EXCEPTION",
            "error": str(exc),
            "ticket": None,
            "order": None,
            "deal": None,
        }

    if result is None:
        return {
            "success": False,
            "sent": False,
            "reason": "ORDER_SEND_RETURNED_NONE",
            "ticket": None,
            "order": None,
            "deal": None,
        }

    retcode = _safe_int(
        getattr(result, "retcode", -1),
        -1,
    )

    success = retcode in {
        getattr(
            mt5,
            "TRADE_RETCODE_DONE",
            10009,
        ),
        getattr(
            mt5,
            "TRADE_RETCODE_DONE_PARTIAL",
            10010,
        ),
    }

    order_ticket = _safe_int(
        getattr(
            result,
            "order",
            0,
        ),
        0,
    )

    deal_ticket = _safe_int(
        getattr(
            result,
            "deal",
            0,
        ),
        0,
    )

    return {
        "success": success,
        "sent": True,
        "paper": False,
        "live": True,
        "blocked": False,
        "reason": (
            "ORDER_SENT"
            if success
            else "ORDER_REJECTED"
        ),
        "retcode": retcode,
        "retcode_name": _retcode_name(
            retcode
        ),
        "ticket": (
            order_ticket
            or deal_ticket
            or None
        ),
        "order": (
            order_ticket
            or None
        ),
        "deal": (
            deal_ticket
            or None
        ),
        "price": _safe_float(
            getattr(
                result,
                "price",
                price_value,
            ),
            price_value,
        ),
        "volume": requested_volume,
        "symbol": symbol,
        "side": side,
        "request": request,
        "comment": str(
            getattr(
                result,
                "comment",
                "",
            )
        ),
    }


# ============================================================
# STATUS
# ============================================================

def get_connector_status() -> Dict[str, Any]:
    account = get_account_snapshot()
    permissions = get_terminal_permissions()

    return {
        "connected": is_connected(),
        "paper_trading": bool(
            PAPER_TRADING
        ),
        "allow_live_trading": bool(
            ALLOW_LIVE_TRADING
        ),
        "live_trading_allowed": live_trading_allowed(),
        "symbol": PILOT_SYMBOL,
        "magic": DEFAULT_MAGIC,
        "max_positions": PROJECT_MAX_POSITIONS,
        "min_lot": PROJECT_MIN_LOT,
        "default_lot": DEFAULT_LOT,
        "max_lot": PROJECT_MAX_LOT,
        "account": account,
        "permissions": permissions,
    }


# ============================================================
# LEGACY / COMPATIBILITY
# ============================================================

def update_trade_status(
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Compatibility placeholder.

    Position state should be read from MT5 itself.
    """

    return {
        "success": False,
        "reason": "MT5_POSITION_STATE_IS_AUTHORITATIVE",
    }


# ============================================================
# CLASS WRAPPER
# ============================================================

class MT5Connector:
    def __init__(
        self,
        symbol: str = PILOT_SYMBOL,
    ) -> None:
        self.symbol = symbol

    def initialize(self) -> bool:
        return initialize_mt5()

    def shutdown(self) -> None:
        shutdown_mt5()

    def is_connected(self) -> bool:
        return is_connected()

    def ensure_connection(self) -> bool:
        return ensure_connection()

    def account_info(self) -> Any:
        return get_account_info()

    def symbol_info(
        self,
        symbol: Optional[str] = None,
    ) -> Any:
        return get_symbol_info(
            symbol or self.symbol
        )

    def tick(
        self,
        symbol: Optional[str] = None,
    ) -> Any:
        return get_symbol_tick(
            symbol or self.symbol
        )

    def rates(
        self,
        timeframe: Any = "M15",
        count: int = 200,
        symbol: Optional[str] = None,
    ) -> Any:
        return get_rates(
            symbol or self.symbol,
            timeframe,
            count,
        )

    def positions(
        self,
        symbol: Optional[str] = None,
    ) -> List[Any]:
        return get_open_positions(
            symbol
        )

    def send_market_order(
        self,
        side: str,
        volume: Optional[float] = None,
        price: Optional[float] = None,
        sl: float = 0.0,
        tp: float = 0.0,
        lot: Optional[float] = None,
    ) -> Dict[str, Any]:
        return send_market_order(
            symbol=self.symbol,
            side=side,
            volume=volume,
            price=price,
            sl=sl,
            tp=tp,
            lot=lot,
        )

    def status(self) -> Dict[str, Any]:
        return get_connector_status()


# Singleton compatibility
MT5 = MT5Connector(
    PILOT_SYMBOL
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

    "PROJECT_MIN_LOT",
    "PROJECT_MAX_LOT",
    "PROJECT_MAX_POSITIONS",

    "initialize_mt5",
    "shutdown_mt5",
    "is_connected",
    "ensure_connection",

    "get_account_info",
    "get_account_snapshot",
    "get_free_margin",

    "get_terminal_permissions",

    "get_symbol_info",
    "get_symbol_tick",
    "get_tick",
    "get_filling_mode",

    "_get_timeframe",
    "get_rates",

    "normalize_price",
    "normalize_volume",

    "validate_stop_distance",

    "get_open_positions",
    "get_project_positions",
    "get_project_position_count",
    "get_open_position_count",
    "validate_position_limit",

    "get_today_realized_profit",
    "get_daily_loss_snapshot",
    "validate_daily_loss_limit",

    "calculate_margin",
    "validate_margin",

    "validate_symbol",
    "validate_volume",

    "live_trading_allowed",
    "send_market_order",

    "get_connector_status",
    "update_trade_status",

    "MT5Connector",
    "MT5",
]
