```python
# core/mt5_connector.py

from __future__ import annotations

import math
import platform
from datetime import datetime, time, timezone
from typing import Any, Dict, Optional

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
# CONSTANTS
# ============================================================

DEFAULT_SYMBOL = PILOT_SYMBOL
DEFAULT_MAGIC = MT5_MAGIC_NUMBER
DEFAULT_DEVIATION = MT5_DEVIATION
DEFAULT_COMMENT = MT5_ORDER_COMMENT

MIN_LOT = MIN_PROJECT_LOT
MAX_LOT = MAX_PROJECT_LOT
MAX_POSITIONS = MAX_OPEN_TRADES


# ============================================================
# CONNECTION
# ============================================================

def initialize_mt5(password: Optional[str] = None) -> bool:
    """
    Initialize the exact portable MT5 terminal used by the project.

    Live trading is NOT enabled here.
    Initialization only establishes the MT5 API connection.
    """

    if platform.system().lower() != "windows":
        return False

    if password is None:
        password = MT5_PASSWORD

    try:
        try:
            mt5.shutdown()
        except Exception:
            pass

        kwargs = {
            "path": MT5_TERMINAL_PATH,
            "portable": MT5_PORTABLE,
            "timeout": MT5_TIMEOUT,
        }

        # Only provide credentials when configured.
        if MT5_LOGIN:
            kwargs["login"] = int(MT5_LOGIN)

        if password:
            kwargs["password"] = password

        if MT5_SERVER:
            kwargs["server"] = MT5_SERVER

        result = mt5.initialize(**kwargs)

        if not result:
            return False

        terminal = mt5.terminal_info()

        if terminal is None:
            return False

        return bool(
            getattr(terminal, "connected", False)
        )

    except Exception:
        return False


def shutdown_mt5() -> None:
    try:
        mt5.shutdown()
    except Exception:
        pass


def is_connected() -> bool:
    try:
        terminal = mt5.terminal_info()

        return bool(
            terminal is not None
            and getattr(terminal, "connected", False)
        )

    except Exception:
        return False


def ensure_connection() -> bool:
    """
    Ensure MT5 is connected.

    No order is sent by this function.
    """

    if is_connected():
        return True

    return initialize_mt5()


# ============================================================
# IDENTITY / ACCOUNT
# ============================================================

def get_account_info():
    try:
        return mt5.account_info()
    except Exception:
        return None


def get_account_snapshot() -> Dict[str, Any]:
    account = get_account_info()

    if account is None:
        return {
            "connected": False,
            "login": None,
            "server": None,
            "balance": None,
            "equity": None,
            "free_margin": None,
            "currency": None,
        }

    return {
        "connected": True,
        "login": getattr(account, "login", None),
        "server": getattr(account, "server", None),
        "balance": float(
            getattr(account, "balance", 0.0) or 0.0
        ),
        "equity": float(
            getattr(account, "equity", 0.0) or 0.0
        ),
        "free_margin": float(
            getattr(account, "margin_free", 0.0) or 0.0
        ),
        "currency": getattr(account, "currency", None),
    }


def verify_account_identity() -> bool:
    account = get_account_info()

    if account is None:
        return False

    login = getattr(account, "login", None)
    server = str(
        getattr(account, "server", "") or ""
    ).strip()

    if MT5_LOGIN and int(login) != int(MT5_LOGIN):
        return False

    if MT5_SERVER and server != MT5_SERVER:
        return False

    return True


# ============================================================
# TERMINAL PERMISSIONS
# ============================================================

def get_terminal_permissions() -> Dict[str, Any]:
    terminal = mt5.terminal_info()

    if terminal is None:
        return {
            "connected": False,
            "trade_allowed": False,
            "trade_expert": False,
            "dlls_allowed": False,
            "tradeapi_disabled": True,
        }

    return {
        "connected": bool(
            getattr(terminal, "connected", False)
        ),
        "trade_allowed": bool(
            getattr(terminal, "trade_allowed", False)
        ),
        "trade_expert": bool(
            getattr(terminal, "trade_expert", False)
        ),
        "dlls_allowed": bool(
            getattr(terminal, "dlls_allowed", False)
        ),
        "tradeapi_disabled": bool(
            getattr(terminal, "tradeapi_disabled", False)
        ),
    }


def live_trading_allowed() -> bool:
    """
    Final project-level live gate.

    Fail closed.
    """

    if PAPER_TRADING:
        return False

    if not ALLOW_LIVE_TRADING:
        return False

    if not ensure_connection():
        return False

    if not verify_account_identity():
        return False

    permissions = get_terminal_permissions()

    if not permissions["connected"]:
        return False

    if not permissions["trade_allowed"]:
        return False

    if not permissions["trade_expert"]:
        return False

    if permissions["tradeapi_disabled"]:
        return False

    return True


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol: str = DEFAULT_SYMBOL,
):
    try:
        if not mt5.symbol_select(symbol, True):
            return None

        return mt5.symbol_info(symbol)

    except Exception:
        return None


def get_symbol_tick(
    symbol: str = DEFAULT_SYMBOL,
):
    try:
        if not mt5.symbol_select(symbol, True):
            return None

        return mt5.symbol_info_tick(symbol)

    except Exception:
        return None


def get_tick(
    symbol: str = DEFAULT_SYMBOL,
):
    return get_symbol_tick(symbol)


# ============================================================
# TIMEFRAME
# ============================================================

def _get_timeframe(timeframe: Any):
    if isinstance(timeframe, int):
        return timeframe

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

    return mapping.get(
        str(timeframe).upper(),
        mt5.TIMEFRAME_M15,
    )


# ============================================================
# MARKET DATA
# ============================================================

def get_rates(
    symbol: str = DEFAULT_SYMBOL,
    timeframe: Any = "M15",
    count: int = 100,
):
    try:
        if not ensure_connection():
            return []

        if not mt5.symbol_select(symbol, True):
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
# NORMALIZATION
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
            getattr(info, "digits", 2) or 2
        )

        return round(float(price), digits)

    except Exception:
        return float(price)


def normalize_volume(
    symbol: str,
    volume: Optional[float] = None,
) -> float:
    """
    Normalize broker volume while respecting project hard limits.

    Compatibility:
        normalize_volume("XAUUSD.su", 0.01)
        normalize_volume(0.01)
    """

    try:
        if volume is None:
            volume = symbol
            symbol = DEFAULT_SYMBOL

        requested = float(volume)

        info = get_symbol_info(symbol)

        if info is None:
            minimum = MIN_LOT
            maximum = MAX_LOT
            step = 0.01
        else:
            broker_min = float(
                getattr(info, "volume_min", MIN_LOT)
                or MIN_LOT
            )

            broker_max = float(
                getattr(info, "volume_max", MAX_LOT)
                or MAX_LOT
            )

            step = float(
                getattr(info, "volume_step", 0.01)
                or 0.01
            )

            minimum = max(
                MIN_LOT,
                broker_min,
            )

            maximum = min(
                MAX_LOT,
                broker_max,
            )

        if minimum > maximum:
            return 0.0

        requested = max(
            minimum,
            min(maximum, requested),
        )

        if step > 0:
            steps = math.floor(
                requested / step
                + 1e-9
            )
            requested = steps * step

        requested = max(
            minimum,
            min(maximum, requested),
        )

        return round(
            requested,
            2,
        )

    except Exception:
        return 0.0


# ============================================================
# FILLING MODE
# ============================================================

def get_filling_mode(
    symbol: str = DEFAULT_SYMBOL,
) -> int:
    try:
        info = get_symbol_info(symbol)

        if info is None:
            return mt5.ORDER_FILLING_IOC

        mode = int(
            getattr(
                info,
                "filling_mode",
                0,
            )
            or 0
        )

        # MT5 symbol filling flags:
        # FOK = 1
        # IOC = 2
        if mode & 2:
            return mt5.ORDER_FILLING_IOC

        if mode & 1:
            return mt5.ORDER_FILLING_FOK

        return mt5.ORDER_FILLING_RETURN

    except Exception:
        return mt5.ORDER_FILLING_IOC


# ============================================================
# POSITIONS
# ============================================================

def get_open_positions(
    symbol: Optional[str] = None,
):
    try:
        if not ensure_connection():
            return []

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


def get_project_positions():
    positions = get_open_positions(
        symbol=PILOT_SYMBOL
    )

    result = []

    for position in positions:
        magic = int(
            getattr(position, "magic", 0)
            or 0
        )

        if magic == int(MT5_MAGIC_NUMBER):
            result.append(position)

    return result


def get_open_position_count(
    symbol: str = PILOT_SYMBOL,
) -> int:
    return len(
        get_open_positions(symbol)
    )


def get_project_position_count() -> int:
    return len(
        get_project_positions()
    )


def validate_position_limit() -> bool:
    return (
        get_project_position_count()
        < MAX_OPEN_TRADES
    )


# ============================================================
# MARGIN
# ============================================================

def get_free_margin() -> float:
    account = get_account_info()

    if account is None:
        return 0.0

    return float(
        getattr(
            account,
            "margin_free",
            0.0,
        )
        or 0.0
    )


def calculate_margin(
    symbol: str,
    side: str,
    volume: float,
    price: Optional[float] = None,
) -> Optional[float]:

    try:
        if not ensure_connection():
            return None

        side = str(side).upper().strip()

        if side == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
        elif side == "SELL":
            order_type = mt5.ORDER_TYPE_SELL
        else:
            return None

        if price is None:
            tick = get_symbol_tick(symbol)

            if tick is None:
                return None

            price = (
                float(tick.ask)
                if side == "BUY"
                else float(tick.bid)
            )

        volume = normalize_volume(
            symbol,
            volume,
        )

        if volume <= 0:
            return None

        result = mt5.order_calc_margin(
            order_type,
            symbol,
            volume,
            float(price),
        )

        if result is None:
            return None

        return float(result)

    except Exception:
        return None


# ============================================================
# DAILY LOSS
# ============================================================

def get_today_realized_profit(
    symbol: Optional[str] = None,
    magic: Optional[int] = None,
) -> float:

    try:
        if not ensure_connection():
            return 0.0

        now = datetime.now()

        start = datetime.combine(
            now.date(),
            time.min,
        )

        end = now

        deals = mt5.history_deals_get(
            start,
            end,
        )

        if deals is None:
            return 0.0

        total = 0.0

        for deal in deals:
            if symbol:
                if getattr(
                    deal,
                    "symbol",
                    "",
                ) != symbol:
                    continue

            if magic is not None:
                if int(
                    getattr(
                        deal,
                        "magic",
                        0,
                    )
                    or 0
                ) != int(magic):
                    continue

            entry = getattr(
                deal,
                "entry",
                None,
            )

            if entry not in (
                mt5.DEAL_ENTRY_OUT,
                mt5.DEAL_ENTRY_OUT_BY,
                mt5.DEAL_ENTRY_INOUT,
            ):
                continue

            profit = float(
                getattr(
                    deal,
                    "profit",
                    0.0,
                )
                or 0.0
            )

            commission = float(
                getattr(
                    deal,
                    "commission",
                    0.0,
                )
                or 0.0
            )

            swap = float(
                getattr(
                    deal,
                    "swap",
                    0.0,
                )
                or 0.0
            )

            fee = float(
                getattr(
                    deal,
                    "fee",
                    0.0,
                )
                or 0.0
            )

            total += (
                profit
                + commission
                + swap
                + fee
            )

        return float(total)

    except Exception:
        return 0.0


def get_daily_loss_snapshot() -> Dict[str, Any]:
    """
    Current-day account/project risk snapshot.

    This is deliberately conservative and does not use
    INITIAL_BALANCE as a live baseline.
    """

    account = get_account_info()

    if account is None:
        return {
            "valid": False,
            "daily_loss_percent": 100.0,
            "daily_loss_amount": 0.0,
            "equity": 0.0,
            "realized_profit": 0.0,
            "floating_profit": 0.0,
            "limit_percent": MAX_DAILY_LOSS_PERCENT,
        }

    equity = float(
        getattr(
            account,
            "equity",
            0.0,
        )
        or 0.0
    )

    balance = float(
        getattr(
            account,
            "balance",
            0.0,
        )
        or 0.0
    )

    realized = get_today_realized_profit(
        symbol=PILOT_SYMBOL,
        magic=MT5_MAGIC_NUMBER,
    )

    project_positions = get_project_positions()

    floating = 0.0

    for position in project_positions:
        floating += float(
            getattr(
                position,
                "profit",
                0.0,
            )
            or 0.0
        )

    # Conservative current-day loss estimate.
    if balance > 0:
        baseline = balance
    elif equity > 0:
        baseline = equity
    else:
        baseline = 1.0

    current_loss_amount = max(
        0.0,
        baseline - equity,
    )

    if current_loss_amount <= 0:
        daily_loss_percent = 0.0
    else:
        daily_loss_percent = (
            current_loss_amount
            / baseline
            * 100.0
        )

    return {
        "valid": True,
        "equity": equity,
        "balance": balance,
        "realized_profit": realized,
        "floating_profit": floating,
        "daily_loss_amount": current_loss_amount,
        "daily_loss_percent": daily_loss_percent,
        "limit_percent": MAX_DAILY_LOSS_PERCENT,
        "within_limit": (
            daily_loss_percent
            < MAX_DAILY_LOSS_PERCENT
        ),
    }


def validate_daily_loss_limit() -> bool:
    snapshot = get_daily_loss_snapshot()

    if not snapshot.get("valid", False):
        return False

    return bool(
        snapshot.get(
            "within_limit",
            False,
        )
    )


# ============================================================
# SL / TP VALIDATION
# ============================================================

def validate_stop_levels(
    symbol: str,
    side: str,
    sl: Optional[float],
    tp: Optional[float],
) -> bool:

    if sl is None or tp is None:
        return False

    tick = get_symbol_tick(symbol)

    if tick is None:
        return False

    side = str(side).upper().strip()

    if side == "BUY":
        price = float(tick.ask)

        if float(sl) >= price:
            return False

        if float(tp) <= price:
            return False

    elif side == "SELL":
        price = float(tick.bid)

        if float(sl) <= price:
            return False

        if float(tp) >= price:
            return False

    else:
        return False

    return True


# ============================================================
# ORDER CHECK
# ============================================================

def order_check(
    request: Dict[str, Any],
):
    try:
        return mt5.order_check(request)
    except Exception:
        return None


def _order_check_success(
    result: Any,
) -> bool:

    if result is None:
        return False

    retcode = int(
        getattr(
            result,
            "retcode",
            0,
        )
        or 0
    )

    return retcode in (
        0,
        mt5.TRADE_RETCODE_DONE,
    )


# ============================================================
# FINAL SAFETY GATE
# ============================================================

def _final_order_gate(
    symbol: str,
    side: str,
    volume: float,
    sl: Optional[float],
    tp: Optional[float],
) -> tuple[bool, str]:

    if PAPER_TRADING:
        return False, "PAPER_TRADING_ACTIVE"

    if not ALLOW_LIVE_TRADING:
        return False, "LIVE_TRADING_DISABLED"

    if not live_trading_allowed():
        return False, "LIVE_GATE_FAILED"

    if symbol != PILOT_SYMBOL:
        return False, "SYMBOL_NOT_ALLOWED"

    if not validate_position_limit():
        return False, "POSITION_LIMIT_REACHED"

    if not validate_daily_loss_limit():
        return False, "DAILY_LOSS_LIMIT"

    normalized = normalize_volume(
        symbol,
        volume,
    )

    if normalized < MIN_LOT:
        return False, "VOLUME_BELOW_MIN"

    if normalized > MAX_LOT:
        return False, "VOLUME_ABOVE_MAX"

    if not validate_stop_levels(
        symbol,
        side,
        sl,
        tp,
    ):
        return False, "INVALID_SL_TP"

    free_margin = get_free_margin()

    if free_margin <= 0:
        return False, "NO_FREE_MARGIN"

    return True, "OK"


# ============================================================
# MARKET ORDER
# ============================================================

def send_market_order(
    symbol: str,
    side: str,
    volume: Optional[float] = None,
    lot: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    magic: int = DEFAULT_MAGIC,
    deviation: int = DEFAULT_DEVIATION,
    comment: str = DEFAULT_COMMENT,
) -> Dict[str, Any]:

    try:
        if volume is None:
            volume = lot

        if volume is None:
            volume = DEFAULT_LOT

        side = str(side).upper().strip()

        if side not in (
            "BUY",
            "SELL",
        ):
            return {
                "success": False,
                "error": "INVALID_SIDE",
                "retcode": None,
            }

        if symbol != PILOT_SYMBOL:
            return {
                "success": False,
                "error": "SYMBOL_NOT_ALLOWED",
                "retcode": None,
            }

        if not ensure_connection():
            return {
                "success": False,
                "error": "MT5_NOT_CONNECTED",
                "retcode": None,
            }

        if not mt5.symbol_select(
            symbol,
            True,
        ):
            return {
                "success": False,
                "error": "SYMBOL_SELECT_FAILED",
                "retcode": None,
            }

        normalized_volume = normalize_volume(
            symbol,
            volume,
        )

        if normalized_volume < MIN_LOT:
            return {
                "success": False,
                "error": "INVALID_VOLUME",
                "retcode": None,
            }

        if normalized_volume > MAX_LOT:
            return {
                "success": False,
                "error": "PROJECT_VOLUME_LIMIT",
                "retcode": None,
            }

        tick = get_symbol_tick(symbol)

        if tick is None:
            return {
                "success": False,
                "error": "NO_TICK",
                "retcode": None,
            }

        if side == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = float(tick.ask)
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = float(tick.bid)

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

        gate_ok, gate_reason = _final_order_gate(
            symbol=symbol,
            side=side,
            volume=normalized_volume,
            sl=sl,
            tp=tp,
        )

        if not gate_ok:
            return {
                "success": False,
                "error": gate_reason,
                "retcode": None,
            }

        filling_mode = get_filling_mode(
            symbol
        )

        request: Dict[str, Any] = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": normalized_volume,
            "type": order_type,
            "price": price,
            "deviation": int(deviation),
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        if sl is not None:
            request["sl"] = sl

        if tp is not None:
            request["tp"] = tp

        check = order_check(request)

        if not _order_check_success(check):
            return {
                "success": False,
                "error": "ORDER_CHECK_FAILED",
                "retcode": getattr(
                    check,
                    "retcode",
                    None,
                ),
                "check": check,
            }

        # IMPORTANT:
        # Exactly ONE order_send call.
        # No automatic retry.
        result = mt5.order_send(
            request
        )

        if result is None:
            return {
                "success": False,
                "error": str(
                    mt5.last_error()
                ),
                "retcode": None,
                "result": None,
            }

        retcode = int(
            getattr(
                result,
                "retcode",
                0,
            )
            or 0
        )

        success = retcode in (
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_DONE_PARTIAL,
        )

        return {
            "success": success,
            "retcode": retcode,
            "order": getattr(
                result,
                "order",
                None,
            ),
            "ticket": getattr(
                result,
                "order",
                None,
            ),
            "deal": getattr(
                result,
                "deal",
                None,
            ),
            "volume": normalized_volume,
            "price": getattr(
                result,
                "price",
                price,
            ),
            "sl": sl,
            "tp": tp,
            "filling_mode": filling_mode,
            "result": result,
            "error": None
            if success
            else str(result),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "retcode": None,
        }


# ============================================================
# CONNECTOR CLASS
# ============================================================

class MT5Connector:

    def __init__(self) -> None:
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

    def ensure_connection(self) -> bool:
        self.initialized = ensure_connection()
        return self.initialized

    def is_connected(self) -> bool:
        return is_connected()

    def get_account_info(self):
        return get_account_info()

    def get_symbol_info(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):
        return get_symbol_info(symbol)

    def get_symbol_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):
        return get_symbol_tick(symbol)

    def get_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ):
        return get_tick(symbol)

    def get_rates(
        self,
        symbol: str = DEFAULT_SYMBOL,
        timeframe: Any = "M15",
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

    def get_open_positions(
        self,
        symbol: Optional[str] = None,
    ):
        return get_open_positions(symbol)

    def get_project_positions(self):
        return get_project_positions()

    def get_open_position_count(
        self,
        symbol: str = PILOT_SYMBOL,
    ) -> int:
        return get_open_position_count(symbol)

    def send_market_order(
        self,
        symbol: str,
        side: str,
        volume: Optional[float] = None,
        lot: Optional[float] = None,
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
            lot=lot,
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
    "initialize_mt5",
    "shutdown_mt5",
    "is_connected",
    "ensure_connection",
    "get_account_info",
    "get_account_snapshot",
    "verify_account_identity",
    "get_terminal_permissions",
    "live_trading_allowed",
    "get_symbol_info",
    "get_symbol_tick",
    "get_tick",
    "get_rates",
    "normalize_price",
    "normalize_volume",
    "get_filling_mode",
    "get_open_positions",
    "get_project_positions",
    "get_open_position_count",
    "get_project_position_count",
    "validate_position_limit",
    "get_free_margin",
    "calculate_margin",
    "get_today_realized_profit",
    "get_daily_loss_snapshot",
    "validate_daily_loss_limit",
    "validate_stop_levels",
    "order_check",
    "send_market_order",
]
```
