# core/mt5_connector.py

from __future__ import annotations

import math
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Tuple

import MetaTrader5 as mt5

from config import (
    ALLOW_LIVE_TRADING,
    DEFAULT_LOT,
    MAX_DAILY_LOSS_PERCENT,
    MAX_OPEN_TRADES,
    MT5_DEVIATION,
    MT5_LOGIN,
    MT5_MAGIC_NUMBER,
    MT5_ORDER_COMMENT,
    MT5_PASSWORD,
    MT5_SERVER,
    MT5_TERMINAL_PATH,
    MT5_PORTABLE,
    MT5_TIMEOUT,
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

MT5_PATH = str(MT5_TERMINAL_PATH)

MT5_LOGIN_TARGET = int(MT5_LOGIN)

MT5_SERVER_TARGET = str(MT5_SERVER).strip()

MT5_PORTABLE_MODE = bool(MT5_PORTABLE)

MT5_CONNECTION_TIMEOUT = int(MT5_TIMEOUT)

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


def _today_start_timestamp() -> int:
    """
    Return today's local midnight timestamp.

    MT5 history uses the terminal's local time context.
    """

    now = datetime.now()

    start = datetime.combine(
        now.date(),
        time.min,
    )

    return int(
        start.timestamp()
    )


# ============================================================
# LIVE TRADING GATE
# ============================================================

def live_trading_allowed() -> bool:
    """
    Final configuration-level live trading gate.

    Real trading requires BOTH:

        ALLOW_LIVE_TRADING=True
        PAPER_TRADING=False

    Fail closed in every other condition.
    """

    try:

        if bool(PAPER_TRADING):
            return False

        if not bool(ALLOW_LIVE_TRADING):
            return False

        return True

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
    Initialize and verify the dedicated portable MT5 terminal.

    The connection is accepted only when:
        - MT5 initializes successfully
        - terminal is connected
        - account information is available
        - expected login matches configured login, when configured
        - expected server matches configured server, when configured

    No order is sent here.
    """

    global _initialized_by_project

    try:

        logger.info("=" * 70)
        logger.info(
            "MT5 CONNECTOR: INITIALIZATION"
        )
        logger.info("=" * 70)

        try:
            mt5.shutdown()

        except Exception:
            pass

        initialized = mt5.initialize(
            path=MT5_PATH,
            portable=MT5_PORTABLE_MODE,
            timeout=MT5_CONNECTION_TIMEOUT,
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

            shutdown_mt5()

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

            shutdown_mt5()

            return False

        account = mt5.account_info()

        if account is None:

            logger.error(
                "MT5 ACCOUNT INFO FAILED | error=%s",
                mt5.last_error(),
            )

            shutdown_mt5()

            return False

        actual_login = _safe_int(
            getattr(
                account,
                "login",
                None,
            )
        )

        actual_server = str(
            getattr(
                account,
                "server",
                "",
            )
        ).strip()

        # ----------------------------------------------------
        # ACCOUNT IDENTITY VERIFICATION
        # ----------------------------------------------------

        if (
            MT5_LOGIN_TARGET > 0
            and actual_login != MT5_LOGIN_TARGET
        ):

            logger.critical(
                "MT5 ACCOUNT BLOCKED | "
                "EXPECTED LOGIN=%s | ACTUAL LOGIN=%s",
                MT5_LOGIN_TARGET,
                actual_login,
            )

            shutdown_mt5()

            return False

        if (
            MT5_SERVER_TARGET
            and actual_server
            and actual_server.lower()
            != MT5_SERVER_TARGET.lower()
        ):

            logger.critical(
                "MT5 SERVER BLOCKED | "
                "EXPECTED=%s | ACTUAL=%s",
                MT5_SERVER_TARGET,
                actual_server,
            )

            shutdown_mt5()

            return False

        _initialized_by_project = True

        logger.info(
            "MT5 INITIALIZATION SUCCESS"
        )

        logger.info(
            "MT5 ACCOUNT | "
            "login=%s | server=%s | "
            "balance=%s | equity=%s | "
            "free_margin=%s | currency=%s",
            getattr(account, "login", None),
            getattr(account, "server", None),
            getattr(account, "balance", None),
            getattr(account, "equity", None),
            getattr(account, "margin_free", None),
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

        logger.info(
            "MT5 PROJECT LIMITS | "
            "MAX_POSITIONS=%s | "
            "MIN_LOT=%s | MAX_LOT=%s",
            PROJECT_MAX_POSITIONS,
            MIN_PROJECT_LOT,
            MAX_PROJECT_LOT,
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

        actual_login = _safe_int(
            getattr(
                account,
                "login",
                None,
            )
        )

        actual_server = str(
            getattr(
                account,
                "server",
                "",
            )
        ).strip()

        if (
            MT5_LOGIN_TARGET > 0
            and actual_login != MT5_LOGIN_TARGET
        ):
            return False

        if (
            MT5_SERVER_TARGET
            and actual_server
            and actual_server.lower()
            != MT5_SERVER_TARGET.lower()
        ):
            return False

        return True

    except Exception:

        return False


def ensure_connection() -> bool:
    """
    Ensure active connection.

    If disconnected, perform one controlled initialization.

    This function NEVER retries an order.
    """

    if is_connected():
        return True

    logger.warning(
        "MT5 CONNECTION LOST - "
        "REINITIALIZING"
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
    Return normalized live account information.

    Actual equity/free margin must be used for risk decisions.
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
# DAILY LOSS CONTROL
# ============================================================

def get_today_realized_profit() -> Optional[float]:
    """
    Return realized P/L from today's MT5 deals.

    This includes the profit/commission/swap fields reported
    by MT5 deals.

    Returns None on data failure.
    """

    try:

        if not ensure_connection():
            return None

        start_timestamp = _today_start_timestamp()

        deals = mt5.history_deals_get(
            start_timestamp,
            datetime.now(),
        )

        if deals is None:
            return None

        total = 0.0

        for deal in deals:

            deal_profit = _safe_float(
                getattr(
                    deal,
                    "profit",
                    0.0,
                )
            )

            commission = _safe_float(
                getattr(
                    deal,
                    "commission",
                    0.0,
                )
            )

            swap = _safe_float(
                getattr(
                    deal,
                    "swap",
                    0.0,
                )
            )

            if deal_profit is None:
                deal_profit = 0.0

            if commission is None:
                commission = 0.0

            if swap is None:
                swap = 0.0

            total += (
                deal_profit
                + commission
                + swap
            )

        return float(total)

    except Exception as exc:

        logger.exception(
            "DAILY REALIZED P/L ERROR: %s",
            exc,
        )

        return None


def get_daily_loss_snapshot() -> Optional[Dict[str, Any]]:
    """
    Return today's realized P/L and current floating P/L.

    This is deliberately conservative.

    The system uses the current live equity as the minimum
    reference available to prevent accepting a loss larger than
    the configured daily percentage when a persistent
    start-of-day equity baseline is not available.

    A future persistent daily baseline can make this stricter
    and more precise.
    """

    account = get_account_snapshot()

    if account is None:
        return None

    realized = get_today_realized_profit()

    if realized is None:
        return None

    floating = _safe_float(
        account.get(
            "profit",
            0.0,
        )
    )

    if floating is None:
        floating = 0.0

    equity = _safe_float(
        account.get(
            "equity",
            0.0,
        )
    )

    if equity is None or equity <= 0:
        return None

    net_today = (
        realized
        + floating
    )

    max_loss_amount = (
        equity
        * (
            float(MAX_DAILY_LOSS_PERCENT)
            / 100.0
        )
    )

    loss_used = max(
        0.0,
        -net_today,
    )

    loss_percent = (
        loss_used
        / equity
        * 100.0
    )

    return {
        "realized": realized,
        "floating": floating,
        "net_today": net_today,
        "equity": equity,
        "loss_used": loss_used,
        "loss_percent": loss_percent,
        "max_loss_percent": float(
            MAX_DAILY_LOSS_PERCENT
        ),
        "max_loss_amount": max_loss_amount,
        "limit_reached": (
            loss_used
            >= max_loss_amount
        ),
    }


def validate_daily_loss_limit() -> Tuple[bool, str]:

    snapshot = (
        get_daily_loss_snapshot()
    )

    if snapshot is None:

        return (
            False,
            "DAILY_LOSS_DATA_UNAVAILABLE",
        )

    if bool(
        snapshot.get(
            "limit_reached",
            False,
        )
    ):

        return (
            False,
            (
                "DAILY_LOSS_LIMIT_REACHED:"
                f"{snapshot['loss_percent']:.2f}%/"
                f"{snapshot['max_loss_percent']:.2f}%"
            ),
        )

    return True, "OK"


# ============================================================
# SYMBOL
# ============================================================

def get_symbol_info(
    symbol: str = DEFAULT_SYMBOL,
) -> Optional[Any]:

    symbol = _normalize_symbol(symbol)

    if not _is_pilot_symbol(symbol):

        logger.error(
            "SYMBOL BLOCKED | "
            "requested=%s | pilot=%s",
            symbol,
            PILOT_SYMBOL,
        )

        return None

    try:

        if not ensure_connection():
            return None

        info = mt5.symbol_info(
            symbol
        )

        if info is None:

            logger.error(
                "SYMBOL INFO FAILED | "
                "symbol=%s | error=%s",
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
                    "SYMBOL SELECT FAILED | "
                    "symbol=%s",
                    symbol,
                )

                return None

            info = mt5.symbol_info(
                symbol
            )

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

        if not mt5.symbol_select(
            symbol,
            True,
        ):
            return None

        tick = mt5.symbol_info_tick(
            symbol
        )

        if tick is None:

            logger.error(
                "SYMBOL TICK FAILED | "
                "symbol=%s | error=%s",
                symbol,
                mt5.last_error(),
            )

            return None

        bid = _safe_float(
            getattr(
                tick,
                "bid",
                None,
            )
        )

        ask = _safe_float(
            getattr(
                tick,
                "ask",
                None,
            )
        )

        if (
            bid is None
            or ask is None
            or bid <= 0
            or ask <= 0
            or ask < bid
        ):

            logger.error(
                "INVALID TICK | "
                "symbol=%s | bid=%s | ask=%s",
                symbol,
                bid,
                ask,
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

        # SYMBOL_FILLING_FOK = 1
        if filling_mode & 1:
            return mt5.ORDER_FILLING_FOK

        # SYMBOL_FILLING_IOC = 2
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

    key = str(
        timeframe
    ).strip()

    return TIMEFRAME_MAP.get(
        key
    )


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
                "COPY RATES FAILED | "
                "symbol=%s | timeframe=%s | "
                "error=%s",
                symbol,
                timeframe,
                mt5.last_error(),
            )

            return None

        if len(rates) == 0:
            return None

        return list(rates)

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

    symbol = _normalize_symbol(
        symbol
    )

    if not _is_pilot_symbol(symbol):
        return None

    value = _safe_float(price)

    if value is None or value <= 0:
        return None

    info = get_symbol_info(
        symbol
    )

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

    symbol = _normalize_symbol(
        symbol
    )

    if not _is_pilot_symbol(symbol):
        return 0.0

    value = _safe_float(
        volume
    )

    if value is None:
        return 0.0

    # NEVER silently cap an oversized request.
    if value > MAX_PROJECT_LOT:

        logger.error(
            "LOT BLOCKED | "
            "requested=%s | max=%s",
            value,
            MAX_PROJECT_LOT,
        )

        return 0.0

    if value < MIN_PROJECT_LOT:

        logger.error(
            "LOT BLOCKED | "
            "requested=%s | min=%s",
            value,
            MIN_PROJECT_LOT,
        )

        return 0.0

    info = get_symbol_info(
        symbol
    )

    if info is None:
        return 0.0

    try:

        broker_min = float(
            getattr(
                info,
                "volume_min",
                MIN_PROJECT_LOT,
            )
        )

        broker_max = float(
            getattr(
                info,
                "volume_max",
                MAX_PROJECT_LOT,
            )
        )

        broker_step = float(
            getattr(
                info,
                "volume_step",
                0.01,
            )
        )

        volume_min = max(
            MIN_PROJECT_LOT,
            broker_min,
        )

        volume_max = min(
            MAX_PROJECT_LOT,
            broker_max,
        )

        if broker_step <= 0:
            broker_step = 0.01

        if (
            volume_min
            > volume_max
        ):
            return 0.0

        if value < volume_min:
            return 0.0

        if value > volume_max:
            return 0.0

        steps = math.floor(
            (
                value
                - volume_min
            )
            / broker_step
            + 1e-9
        )

        normalized = (
            volume_min
            + steps * broker_step
        )

        normalized = round(
            normalized,
            8,
        )

        if (
            normalized
            < MIN_PROJECT_LOT
        ):
            return 0.0

        if (
            normalized
            > MAX_PROJECT_LOT
        ):
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

    info = get_symbol_info(
        symbol
    )

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

    symbol = _normalize_symbol(
        symbol
    )

    side = str(
        side
    ).strip().upper()

    if not _is_pilot_symbol(
        symbol
    ):
        return (
            False,
            "PILOT_SYMBOL_ONLY",
        )

    entry_value = _safe_float(
        entry
    )

    sl_value = _safe_float(
        sl
    )

    tp_value = _safe_float(
        tp
    )

    if (
        entry_value is None
        or sl_value is None
        or tp_value is None
    ):
        return (
            False,
            "INVALID_PRICE",
        )

    if (
        entry_value <= 0
        or sl_value <= 0
        or tp_value <= 0
    ):
        return (
            False,
            "NON_POSITIVE_PRICE",
        )

    minimum_distance = (
        get_stop_freeze_distance(
            symbol
        )
    )

    if side == "BUY":

        if sl_value >= entry_value:
            return (
                False,
                "BUY_SL_NOT_BELOW_ENTRY",
            )

        if tp_value <= entry_value:
            return (
                False,
                "BUY_TP_NOT_ABOVE_ENTRY",
            )

        if minimum_distance > 0:

            if (
                entry_value
                - sl_value
                < minimum_distance
            ):
                return (
                    False,
                    "BUY_SL_TOO_CLOSE",
                )

            if (
                tp_value
                - entry_value
                < minimum_distance
            ):
                return (
                    False,
                    "BUY_TP_TOO_CLOSE",
                )

    elif side == "SELL":

        if sl_value <= entry_value:
            return (
                False,
                "SELL_SL_NOT_ABOVE_ENTRY",
            )

        if tp_value >= entry_value:
            return (
                False,
                "SELL_TP_NOT_BELOW_ENTRY",
            )

        if minimum_distance > 0:

            if (
                sl_value
                - entry_value
                < minimum_distance
            ):
                return (
                    False,
                    "SELL_SL_TOO_CLOSE",
                )

            if (
                entry_value
                - tp_value
                < minimum_distance
            ):
                return (
                    False,
                    "SELL_TP_TOO_CLOSE",
                )

    else:

        return (
            False,
            "INVALID_SIDE",
        )

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

            symbol = _normalize_symbol(
                symbol
            )

            if not _is_pilot_symbol(
                symbol
            ):
                return []

            positions = (
                mt5.positions_get(
                    symbol=symbol
                )
            )

        else:

            positions = (
                mt5.positions_get()
            )

        if positions is None:
            return []

        return list(
            positions
        )

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

    if not _is_pilot_symbol(
        symbol
    ):
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
                "PROJECT_POSITION_LIMIT_REACHED:"
                f"{count}/"
                f"{PROJECT_MAX_POSITIONS}"
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

    symbol = _normalize_symbol(
        symbol
    )

    side = str(
        side
    ).strip().upper()

    if not _is_pilot_symbol(
        symbol
    ):
        return None

    if side == "BUY":

        order_type = (
            mt5.ORDER_TYPE_BUY
        )

    elif side == "SELL":

        order_type = (
            mt5.ORDER_TYPE_SELL
        )

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

        result_value = _safe_float(
            result
        )

        if (
            result_value is None
            or result_value < 0
        ):
            return None

        return result_value

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

        return (
            False,
            "ACCOUNT_UNAVAILABLE",
        )

    margin = calculate_margin(
        symbol,
        side,
        volume,
        price,
    )

    if margin is None:

        return (
            False,
            "MARGIN_CALC_FAILED",
        )

    free_margin = _safe_float(
        getattr(
            account,
            "margin_free",
            0.0,
        )
    )

    if free_margin is None:

        return (
            False,
            "FREE_MARGIN_UNAVAILABLE",
        )

    if margin > free_margin:

        return (
            False,
            (
                "INSUFFICIENT_MARGIN:"
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

    side = str(
        side
    ).strip().upper()

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

    symbol = _normalize_symbol(
        symbol
    )

    side = str(
        side
    ).strip().upper()

    if not _is_pilot_symbol(
        symbol
    ):
        return None

    order_type = _get_order_type(
        side
    )

    if order_type is None:
        return None

    tick = get_symbol_tick(
        symbol
    )

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

    if (
        price is None
        or price <= 0
    ):
        return None

    normalized_volume = (
        normalize_volume(
            symbol,
            volume,
        )
    )

    if normalized_volume <= 0:
        return None

    normalized_sl = (
        normalize_price(
            symbol,
            sl,
        )
    )

    normalized_tp = (
        normalize_price(
            symbol,
            tp,
        )
    )

    if (
        normalized_sl is None
        or normalized_tp is None
    ):
        return None

    valid, reason = (
        validate_sl_tp(
            symbol=symbol,
            side=side,
            entry=price,
            sl=normalized_sl,
            tp=normalized_tp,
        )
    )

    if not valid:

        logger.error(
            "ORDER REQUEST BLOCKED | "
            "SL/TP | reason=%s",
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
        "type_filling": get_filling_mode(
            symbol
        ),
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

        retcode = int(
            retcode
        )

    except Exception:

        return False

    return (
        retcode
        == mt5.TRADE_RETCODE_DONE
    )


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
) -> Tuple[
    bool,
    Optional[Dict[str, Any]],
    str,
]:

    symbol = _normalize_symbol(
        symbol
    )

    side = str(
        side
    ).strip().upper()

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
    # LIVE GATE
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
    # SYMBOL
    # --------------------------------------------------------

    if not _is_pilot_symbol(
        symbol
    ):

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
    # DAILY LOSS LIMIT
    # --------------------------------------------------------

    daily_ok, daily_reason = (
        validate_daily_loss_limit()
    )

    if not daily_ok:

        return (
            False,
            None,
            daily_reason,
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
        requested_volume
        < MIN_PROJECT_LOT
    ):

        return (
            False,
            None,
            "VOLUME_BELOW_PROJECT_MIN",
        )

    if (
        requested_volume
        > MAX_PROJECT_LOT
    ):

        return (
            False,
            None,
            "VOLUME_ABOVE_PROJECT_MAX",
        )

    normalized_volume = (
        normalize_volume(
            symbol,
            requested_volume,
        )
    )

    if normalized_volume <= 0:

        return (
            False,
            None,
            "VOLUME_NORMALIZATION_FAILED",
        )

    # --------------------------------------------------------
    # ENTRY PRICE
    # --------------------------------------------------------

    tick = get_symbol_tick(
        symbol
    )

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

    if (
        entry is None
        or entry <= 0
    ):

        return (
            False,
            None,
            "INVALID_ENTRY_PRICE",
        )

    # --------------------------------------------------------
    # SL / TP
    # --------------------------------------------------------

    normalized_sl = (
        normalize_price(
            symbol,
            sl,
        )
    )

    normalized_tp = (
        normalize_price(
            symbol,
            tp,
        )
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

    try:

        check_result = (
            mt5.order_check(
                request
            )
        )

    except Exception as exc:

        logger.exception(
            "MT5 ORDER CHECK EXCEPTION: %s",
            exc,
        )

        return (
            False,
            None,
            "ORDER_CHECK_EXCEPTION",
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
                f"comment="
                f"{getattr(check_result, 'comment', '')}"
            ),
        )

    logger.info(
        "FINAL ORDER CHECK PASSED | "
        "symbol=%s | side=%s | "
        "volume=%s | entry=%s | "
        "sl=%s | tp=%s",
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
    volume: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    magic: int = DEFAULT_MAGIC,
    comment: str = DEFAULT_COMMENT,
    lot: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Send exactly ONE market order.

    IMPORTANT:

    - Paper trading blocks all real execution.
    - Live trading requires both live flags.
    - No automatic retry exists after order_send().
    - An ambiguous result is never automatically retried.
    - Project lot hard limit is 0.03.
    - Project position limit is 5.
    - order_check() must pass before order_send().
    """

    # --------------------------------------------------------
    # COMPATIBILITY: lot= alias
    # --------------------------------------------------------

    if volume is None:

        volume = lot

    if volume is None:

        volume = DEFAULT_LOT

    if sl is None or tp is None:

        return {
            "success": False,
            "status": "BLOCKED",
            "reason": "SL_TP_REQUIRED",
            "ticket": None,
            "order": None,
            "deal": None,
            "retcode": None,
            "result": None,
        }

    # --------------------------------------------------------
    # PAPER MODE HARD STOP
    # --------------------------------------------------------

    if bool(PAPER_TRADING):

        logger.info(
            "MT5 ORDER BLOCKED | "
            "PAPER_TRADING=True | "
            "NO REAL ORDER SEND"
        )

        return {
            "success": False,
            "status": "PAPER_BLOCKED",
            "reason": "PAPER_TRADING_ENABLED",
            "ticket": None,
            "order": None,
            "deal": None,
            "retcode": None,
            "result": None,
        }

    # --------------------------------------------------------
    # LIVE FLAG HARD STOP
    # --------------------------------------------------------

    if not bool(ALLOW_LIVE_TRADING):

        logger.warning(
            "MT5 ORDER BLOCKED | "
            "ALLOW_LIVE_TRADING=False"
        )

        return {
            "success": False,
            "status": "LIVE_BLOCKED",
            "reason": "ALLOW_LIVE_TRADING_FALSE",
            "ticket": None,
            "order": None,
            "deal": None,
            "retcode": None,
            "result": None,
        }

    # --------------------------------------------------------
    # FINAL SAFETY GATE
    # --------------------------------------------------------

    gate_ok, request, reason = (
        check_market_order(
            symbol=symbol,
            side=side,
            volume=float(volume),
            sl=float(sl),
            tp=float(tp),
            magic=magic,
            comment=comment,
        )
    )

    if not gate_ok:

        logger.warning(
            "MARKET ORDER BLOCKED | "
            "reason=%s",
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
            "result": None,
        }

    # --------------------------------------------------------
    # EXACTLY ONE ORDER_SEND
    # --------------------------------------------------------

    try:

        logger.warning(
            "MT5 ORDER SEND | "
            "symbol=%s | side=%s | "
            "volume=%s | sl=%s | tp=%s",
            symbol,
            side,
            request.get("volume"),
            request.get("sl"),
            request.get("tp"),
        )

        result = mt5.order_send(
            request
        )

    except Exception as exc:

        logger.exception(
            "MT5 ORDER SEND EXCEPTION | "
            "NO AUTOMATIC RETRY: %s",
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
            "result": None,
        }

    # --------------------------------------------------------
    # AMBIGUOUS RESULT
    # --------------------------------------------------------

    if result is None:

        logger.error(
            "MT5 ORDER SEND RETURNED NONE | "
            "NO AUTOMATIC RETRY | "
            "error=%s",
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
            "result": None,
        }

    # --------------------------------------------------------
    # RESULT EXTRACTION
    # --------------------------------------------------------

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

    try:

        retcode_int = int(
            retcode
        )

    except Exception:

        retcode_int = None

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    success_codes = {
        int(
            mt5.TRADE_RETCODE_DONE
        ),
        int(
            mt5.TRADE_RETCODE_DONE_PARTIAL
        ),
    }

    if retcode_int in success_codes:

        ticket = (
            deal_ticket
            or order_ticket
        )

        logger.info(
            "MT5 ORDER SUCCESS | "
            "retcode=%s | "
            "order=%s | deal=%s",
            retcode_int,
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
            "retcode": retcode_int,
            "result": result,
        }

    # --------------------------------------------------------
    # FAILED ORDER
    # --------------------------------------------------------

    logger.error(
        "MT5 ORDER FAILED | "
        "retcode=%s | comment=%s",
        retcode_int,
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
        "retcode": retcode_int,
        "result": result,
    }


# ============================================================
# COMPATIBILITY TRADE STATUS
# ============================================================

def update_trade_status(
    ticket: int,
    status: str,
) -> bool:

    logger.info(
        "TRADE STATUS | "
        "ticket=%s | status=%s",
        ticket,
        status,
    )

    return True


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

def get_tick(
    symbol: str = DEFAULT_SYMBOL,
) -> Optional[Any]:
    """
    Backward-compatible alias used by legacy modules.
    """

    return get_symbol_tick(
        symbol
    )


# ============================================================
# CONNECTOR CLASS
# ============================================================

class MT5Connector:
    """
    Object-oriented compatibility wrapper.
    """

    def __init__(
        self,
        path: str = MT5_PATH,
        portable: bool = MT5_PORTABLE_MODE,
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

    def live_trading_allowed(self) -> bool:

        return live_trading_allowed()

    def get_account_info(
        self,
    ) -> Optional[Any]:

        return get_account_info()

    def get_account_snapshot(
        self,
    ) -> Optional[Dict[str, Any]]:

        return get_account_snapshot()

    def get_account_trading_permissions(
        self,
    ) -> Dict[str, bool]:

        return get_account_trading_permissions()

    def get_symbol_info(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> Optional[Any]:

        return get_symbol_info(
            symbol
        )

    def get_symbol_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> Optional[Any]:

        return get_symbol_tick(
            symbol
        )

    def get_tick(
        self,
        symbol: str = DEFAULT_SYMBOL,
    ) -> Optional[Any]:

        return get_symbol_tick(
            symbol
        )

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

        return get_open_positions(
            symbol
        )

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

    def calculate_margin(
        self,
        symbol: str,
        side: str,
        volume: float,
        price: float,
    ) -> Optional[float]:

        return calculate_margin(
            symbol,
            side,
            volume,
            price,
        )

    def validate_daily_loss_limit(
        self,
    ) -> Tuple[bool, str]:

        return validate_daily_loss_limit()

    def send_market_order(
        self,
        symbol: str,
        side: str,
        volume: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        magic: int = DEFAULT_MAGIC,
        comment: str = DEFAULT_COMMENT,
        lot: Optional[float] = None,
    ) -> Dict[str, Any]:

        return send_market_order(
            symbol=symbol,
            side=side,
            volume=volume,
            sl=sl,
            tp=tp,
            magic=magic,
            comment=comment,
            lot=lot,
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
    "MT5_LOGIN_TARGET",
    "MT5_SERVER_TARGET",
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
    "get_today_realized_profit",
    "get_daily_loss_snapshot",
    "validate_daily_loss_limit",
    "get_symbol_info",
    "get_symbol_tick",
    "get_tick",
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
