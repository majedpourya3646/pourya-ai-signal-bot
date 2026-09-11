# core/position_manager.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

import MetaTrader5 as mt5

from core.logger import logger
from core.mt5_connector import (
    ensure_connection,
    get_open_positions,
    get_symbol_info,
    get_symbol_tick,
    get_rates,
    normalize_price,
)

from config import (
    ALLOW_LIVE_TRADING,
    PAPER_TRADING,
)


# ============================================================
# CONFIG
# ============================================================

MAGIC_NUMBER = 20260731
DEVIATION = 20

# Pilot symbol
PILOT_SYMBOL = "XAUUSD.su"

# Automatic SL / TP
ENABLE_AUTO_SL_TP = True

ATR_TIMEFRAME = mt5.TIMEFRAME_M15
ATR_PERIOD = 14

ATR_SL_MULTIPLIER = 1.5
ATR_TP_MULTIPLIER = 3.0

# Break Even
ENABLE_BREAK_EVEN = True
BREAK_EVEN_TRIGGER_PERCENT = 1.0
BREAK_EVEN_OFFSET_PERCENT = 0.05

# Trailing Stop
ENABLE_TRAILING_STOP = True
TRAILING_START_PERCENT = 1.5
TRAILING_DISTANCE_PERCENT = 0.75

ORDER_COMMENT_SLTP = "Pourya AI SLTP"
ORDER_COMMENT_CLOSE = "Pourya AI Close"


# ============================================================
# SYMBOL HELPERS
# ============================================================

def _normalize_symbol(
    symbol: Any,
) -> str:

    if symbol is None:
        return ""

    return str(symbol).strip().upper()


def _is_pilot_symbol(
    symbol: Any,
) -> bool:

    return (
        _normalize_symbol(symbol)
        == _normalize_symbol(PILOT_SYMBOL)
    )


# ============================================================
# LIVE TRADING SAFETY
# ============================================================

def _live_trading_allowed() -> bool:
    """
    Independent safety gate for any real MT5 modification.

    Real MT5 modifications are allowed only when:

        PAPER_TRADING == False
        ALLOW_LIVE_TRADING == True

    Any configuration error fails closed.
    """

    try:

        if PAPER_TRADING:

            logger.warning(
                "POSITION MANAGER: "
                "PAPER_TRADING=True - "
                "REAL MT5 MODIFICATION BLOCKED"
            )

            return False

        if not ALLOW_LIVE_TRADING:

            logger.critical(
                "POSITION MANAGER: "
                "ALLOW_LIVE_TRADING=False - "
                "REAL MT5 MODIFICATION BLOCKED"
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "POSITION MANAGER LIVE SAFETY ERROR %s",
            exc,
        )

        return False


# ============================================================
# GENERIC HELPERS
# ============================================================

def _get_value(
    obj: Any,
    key: str,
    default: Any = None,
) -> Any:

    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(
            key,
            default,
        )

    try:

        return getattr(
            obj,
            key,
        )

    except AttributeError:

        return default


def _position_ticket(
    position: Any,
) -> Optional[int]:

    value = _get_value(
        position,
        "ticket",
    )

    if value is None:
        return None

    try:
        return int(value)

    except Exception:
        return None


def _position_magic(
    position: Any,
) -> Optional[int]:

    value = _get_value(
        position,
        "magic",
    )

    if value is None:
        return None

    try:
        return int(value)

    except Exception:
        return None


def _position_symbol(
    position: Any,
) -> Optional[str]:

    value = _get_value(
        position,
        "symbol",
    )

    if value is None:
        return None

    return str(value)


def _position_type(
    position: Any,
) -> Optional[int]:

    value = _get_value(
        position,
        "type",
    )

    if value is None:
        return None

    try:
        return int(value)

    except Exception:
        return None


def _position_volume(
    position: Any,
) -> float:

    value = _get_value(
        position,
        "volume",
        0.0,
    )

    try:
        return float(value)

    except Exception:
        return 0.0


def _position_price_open(
    position: Any,
) -> float:

    value = _get_value(
        position,
        "price_open",
        0.0,
    )

    try:
        return float(value)

    except Exception:
        return 0.0


def _position_sl(
    position: Any,
) -> float:

    value = _get_value(
        position,
        "sl",
        0.0,
    )

    try:
        return float(value)

    except Exception:
        return 0.0


def _position_tp(
    position: Any,
) -> float:

    value = _get_value(
        position,
        "tp",
        0.0,
    )

    try:
        return float(value)

    except Exception:
        return 0.0


def _is_buy_position(
    position: Any,
) -> bool:

    return (
        _position_type(position)
        == mt5.POSITION_TYPE_BUY
    )


def _is_sell_position(
    position: Any,
) -> bool:

    return (
        _position_type(position)
        == mt5.POSITION_TYPE_SELL
    )


def is_buy_position(
    position: Any,
) -> bool:

    return _is_buy_position(
        position
    )


def is_sell_position(
    position: Any,
) -> bool:

    return _is_sell_position(
        position
    )


# ============================================================
# CONNECTION
# ============================================================

def _ensure_mt5() -> bool:
    """
    Always use the centralized MT5 connector.

    Portable terminal:

        C:\\MT5-Pourya\\terminal64.exe
    """

    try:

        return bool(
            ensure_connection()
        )

    except Exception as exc:

        logger.exception(
            "POSITION MANAGER MT5 CONNECTION ERROR %s",
            exc,
        )

        return False


# ============================================================
# POSITION SAFETY VALIDATION
# ============================================================

def _validate_project_position(
    position: Any,
) -> bool:
    """
    Verify that a position belongs to the current
    Pourya Trader AI pilot.

    Required:
        - XAUUSD.su
        - MAGIC_NUMBER
        - valid ticket
        - valid BUY/SELL type
        - positive volume
    """

    if position is None:
        return False

    ticket = _position_ticket(
        position
    )

    symbol = _position_symbol(
        position
    )

    magic = _position_magic(
        position
    )

    position_type = _position_type(
        position
    )

    volume = _position_volume(
        position
    )

    if ticket is None:
        return False

    if not _is_pilot_symbol(symbol):
        return False

    if magic != MAGIC_NUMBER:
        return False

    if position_type not in (
        mt5.POSITION_TYPE_BUY,
        mt5.POSITION_TYPE_SELL,
    ):
        return False

    if volume <= 0:
        return False

    return True


def _get_position_by_ticket(
    ticket: int,
) -> Optional[Any]:

    try:

        positions = mt5.positions_get(
            ticket=int(ticket)
        )

        if not positions:
            return None

        return positions[0]

    except Exception as exc:

        logger.exception(
            "GET POSITION ERROR "
            "TICKET=%s ERROR=%s",
            ticket,
            exc,
        )

        return None


# ============================================================
# ATR
# ============================================================

def calculate_atr(
    symbol: str,
    timeframe: int = ATR_TIMEFRAME,
    period: int = ATR_PERIOD,
) -> Optional[float]:

    try:

        if not _is_pilot_symbol(symbol):

            logger.warning(
                "ATR BLOCKED - "
                "NON-PILOT SYMBOL=%s",
                symbol,
            )

            return None

        if not _ensure_mt5():

            logger.warning(
                "ATR: MT5 NOT CONNECTED"
            )

            return None

        bars_needed = max(
            period + 5,
            30,
        )

        rates = get_rates(
            symbol=symbol,
            timeframe=timeframe,
            count=bars_needed,
        )

        if rates is None:

            logger.warning(
                "ATR: NO DATA SYMBOL=%s TIMEFRAME=%s",
                symbol,
                timeframe,
            )

            return None

        if len(rates) < period + 1:

            logger.warning(
                "ATR: NOT ENOUGH DATA "
                "SYMBOL=%s COUNT=%s REQUIRED=%s",
                symbol,
                len(rates),
                period + 1,
            )

            return None

        true_ranges: List[float] = []

        for i in range(
            1,
            len(rates),
        ):

            current = rates[i]
            previous = rates[i - 1]

            high = float(
                current["high"]
            )

            low = float(
                current["low"]
            )

            previous_close = float(
                previous["close"]
            )

            tr = max(
                high - low,
                abs(
                    high
                    - previous_close
                ),
                abs(
                    low
                    - previous_close
                ),
            )

            true_ranges.append(
                tr
            )

        if len(true_ranges) < period:
            return None

        recent_tr = true_ranges[
            -period:
        ]

        atr = (
            sum(recent_tr)
            / len(recent_tr)
        )

        if atr <= 0:
            return None

        return float(atr)

    except Exception as exc:

        logger.exception(
            "ATR CALCULATION ERROR %s",
            exc,
        )

        return None


# ============================================================
# BROKER STOP DISTANCE
# ============================================================

def get_min_stop_distance(
    symbol: str,
) -> float:

    try:

        if not _is_pilot_symbol(symbol):
            return 0.0

        if not _ensure_mt5():
            return 0.0

        info = get_symbol_info(
            symbol
        )

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

        if point <= 0 or level <= 0:
            return 0.0

        return float(
            level * point
        )

    except Exception as exc:

        logger.exception(
            "STOP DISTANCE ERROR SYMBOL=%s ERROR=%s",
            symbol,
            exc,
        )

        return 0.0


# ============================================================
# SL / TP VALIDATION
# ============================================================

def validate_sl_tp(
    symbol: str,
    position_type: int,
    sl: float,
    tp: float,
) -> bool:

    try:

        if not _is_pilot_symbol(symbol):
            return False

        if not _ensure_mt5():
            return False

        if sl <= 0 or tp <= 0:
            return False

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return False

        bid = float(
            getattr(
                tick,
                "bid",
                0.0,
            )
            or 0.0
        )

        ask = float(
            getattr(
                tick,
                "ask",
                0.0,
            )
            or 0.0
        )

        if bid <= 0 or ask <= 0:
            return False

        min_distance = (
            get_min_stop_distance(
                symbol
            )
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            reference_price = bid

            if sl >= reference_price:
                return False

            if tp <= reference_price:
                return False

            if min_distance > 0:

                if (
                    reference_price - sl
                ) < min_distance:

                    return False

                if (
                    tp - reference_price
                ) < min_distance:

                    return False

            return True

        if position_type == mt5.POSITION_TYPE_SELL:

            reference_price = ask

            if sl <= reference_price:
                return False

            if tp >= reference_price:
                return False

            if min_distance > 0:

                if (
                    sl - reference_price
                ) < min_distance:

                    return False

                if (
                    reference_price - tp
                ) < min_distance:

                    return False

            return True

        return False

    except Exception as exc:

        logger.exception(
            "SL TP VALIDATION ERROR "
            "SYMBOL=%s ERROR=%s",
            symbol,
            exc,
        )

        return False


# ============================================================
# ATR SL / TP CALCULATION
# ============================================================

def calculate_atr_sl_tp(
    symbol: str,
    position_type: int,
    entry_price: float,
    atr: Optional[float] = None,
) -> Optional[Dict[str, float]]:

    try:

        if not _is_pilot_symbol(symbol):
            return None

        if not _ensure_mt5():
            return None

        if entry_price <= 0:
            return None

        if atr is None:

            atr = calculate_atr(
                symbol
            )

        if atr is None or atr <= 0:
            return None

        sl_distance = (
            atr
            * ATR_SL_MULTIPLIER
        )

        tp_distance = (
            atr
            * ATR_TP_MULTIPLIER
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            sl = (
                entry_price
                - sl_distance
            )

            tp = (
                entry_price
                + tp_distance
            )

        elif position_type == mt5.POSITION_TYPE_SELL:

            sl = (
                entry_price
                + sl_distance
            )

            tp = (
                entry_price
                - tp_distance
            )

        else:

            return None

        sl = normalize_price(
            symbol,
            sl,
        )

        tp = normalize_price(
            symbol,
            tp,
        )

        if sl is None or tp is None:
            return None

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=sl,
            tp=tp,
        ):

            logger.warning(
                "ATR SL/TP INVALID "
                "SYMBOL=%s TYPE=%s SL=%.5f TP=%.5f",
                symbol,
                position_type,
                sl,
                tp,
            )

            return None

        return {
            "sl": float(sl),
            "tp": float(tp),
            "atr": float(atr),
            "sl_distance": float(
                sl_distance
            ),
            "tp_distance": float(
                tp_distance
            ),
        }

    except Exception as exc:

        logger.exception(
            "ATR SL TP CALCULATION ERROR "
            "SYMBOL=%s ERROR=%s",
            symbol,
            exc,
        )

        return None


# ============================================================
# ORDER CHECK HELPER
# ============================================================

def _order_check(
    request: Dict[str, Any],
    operation: str,
) -> bool:

    try:

        result = mt5.order_check(
            request
        )

        if result is None:

            logger.error(
                "%s ORDER_CHECK FAILED "
                "ERROR=%s",
                operation,
                mt5.last_error(),
            )

            return False

        retcode = int(
            getattr(
                result,
                "retcode",
                0,
            )
            or 0
        )

        if retcode != 0:

            logger.error(
                "%s ORDER_CHECK REJECTED "
                "RETCODE=%s COMMENT=%s",
                operation,
                retcode,
                getattr(
                    result,
                    "comment",
                    "",
                ),
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            "%s ORDER_CHECK ERROR %s",
            operation,
            exc,
        )

        return False


# ============================================================
# MODIFY POSITION SL / TP
# ============================================================

def modify_position_sl_tp(
    ticket: int,
    symbol: str,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
) -> bool:

    try:

        if not _is_pilot_symbol(symbol):

            logger.warning(
                "MODIFY SLTP BLOCKED - "
                "NON-PILOT SYMBOL=%s",
                symbol,
            )

            return False

        if not _ensure_mt5():

            logger.warning(
                "MODIFY SLTP: MT5 NOT CONNECTED"
            )

            return False

        if not _live_trading_allowed():

            logger.warning(
                "MODIFY SLTP: "
                "REAL MT5 MODIFICATION BLOCKED "
                "TICKET=%s",
                ticket,
            )

            return False

        position = _get_position_by_ticket(
            ticket
        )

        if position is None:

            logger.warning(
                "MODIFY SLTP: "
                "POSITION NOT FOUND TICKET=%s",
                ticket,
            )

            return False

        if not _validate_project_position(
            position
        ):

            logger.warning(
                "MODIFY SLTP BLOCKED - "
                "POSITION SAFETY VALIDATION FAILED "
                "TICKET=%s",
                ticket,
            )

            return False

        actual_symbol = _position_symbol(
            position
        )

        if not _is_pilot_symbol(actual_symbol):

            return False

        position_type = _position_type(
            position
        )

        current_sl = _position_sl(
            position
        )

        current_tp = _position_tp(
            position
        )

        if sl is None:
            sl = current_sl

        if tp is None:
            tp = current_tp

        sl = float(
            sl or 0.0
        )

        tp = float(
            tp or 0.0
        )

        if sl <= 0 or tp <= 0:

            logger.warning(
                "MODIFY SLTP BLOCKED - "
                "INVALID SL/TP "
                "TICKET=%s SL=%s TP=%s",
                ticket,
                sl,
                tp,
            )

            return False

        if not validate_sl_tp(
            symbol=actual_symbol,
            position_type=position_type,
            sl=sl,
            tp=tp,
        ):

            logger.warning(
                "MODIFY SLTP BLOCKED - "
                "SL/TP VALIDATION FAILED "
                "TICKET=%s SL=%.5f TP=%.5f",
                ticket,
                sl,
                tp,
            )

            return False

        sl = normalize_price(
            actual_symbol,
            sl,
        )

        tp = normalize_price(
            actual_symbol,
            tp,
        )

        if sl is None or tp is None:
            return False

        request = {
            "action":
                mt5.TRADE_ACTION_SLTP,

            "position":
                int(ticket),

            "symbol":
                actual_symbol,

            "sl":
                float(sl),

            "tp":
                float(tp),

            "magic":
                MAGIC_NUMBER,

            "comment":
                ORDER_COMMENT_SLTP,
        }

        # ----------------------------------------------------
        # PRE-FLIGHT ORDER CHECK
        # ----------------------------------------------------

        if not _order_check(
            request,
            "MODIFY SLTP",
        ):

            return False

        logger.info(
            "MODIFY SLTP: SEND "
            "TICKET=%s SYMBOL=%s "
            "SL=%.5f TP=%.5f",
            ticket,
            actual_symbol,
            sl,
            tp,
        )

        # ----------------------------------------------------
        # SINGLE SEND - NO BLIND RETRY
        # ----------------------------------------------------

        result = mt5.order_send(
            request
        )

        if result is None:

            logger.error(
                "MODIFY SLTP FAILED "
                "TICKET=%s ERROR=%s",
                ticket,
                mt5.last_error(),
            )

            return False

        retcode = int(
            getattr(
                result,
                "retcode",
                0,
            )
            or 0
        )

        if retcode != mt5.TRADE_RETCODE_DONE:

            logger.error(
                "MODIFY SLTP REJECTED "
                "TICKET=%s RETCODE=%s COMMENT=%s",
                ticket,
                retcode,
                getattr(
                    result,
                    "comment",
                    "",
                ),
            )

            return False

        logger.info(
            "SL/TP UPDATED "
            "TICKET=%s SYMBOL=%s "
            "SL=%.5f TP=%.5f RETCODE=%s",
            ticket,
            actual_symbol,
            sl,
            tp,
            retcode,
        )

        return True

    except Exception as exc:

        logger.exception(
            "MODIFY SLTP ERROR "
            "TICKET=%s ERROR=%s",
            ticket,
            exc,
        )

        return False


# ============================================================
# CLOSE POSITION
# ============================================================

def close_position(
    ticket: int,
) -> bool:
    """
    Close an existing Pourya Trader AI position.

    Safety requirements:
        - XAUUSD.su only
        - MAGIC_NUMBER must match
        - PAPER_TRADING must be False
        - ALLOW_LIVE_TRADING must be True
        - order_check must pass
        - exactly one order_send attempt
    """

    try:

        if ticket is None:

            logger.warning(
                "CLOSE POSITION: "
                "INVALID TICKET=None"
            )

            return False

        if not _ensure_mt5():

            logger.warning(
                "CLOSE POSITION: "
                "MT5 NOT CONNECTED "
                "TICKET=%s",
                ticket,
            )

            return False

        position = _get_position_by_ticket(
            ticket
        )

        if position is None:

            logger.warning(
                "CLOSE POSITION: "
                "POSITION NOT FOUND "
                "TICKET=%s",
                ticket,
            )

            return False

        if not _validate_project_position(
            position
        ):

            logger.warning(
                "CLOSE POSITION BLOCKED - "
                "POSITION SAFETY VALIDATION FAILED "
                "TICKET=%s",
                ticket,
            )

            return False

        symbol = _position_symbol(
            position
        )

        position_type = _position_type(
            position
        )

        volume = _position_volume(
            position
        )

        if not symbol or volume <= 0:
            return False

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            logger.warning(
                "CLOSE POSITION: "
                "NO TICK SYMBOL=%s TICKET=%s",
                symbol,
                ticket,
            )

            return False

        bid = float(
            getattr(
                tick,
                "bid",
                0.0,
            )
            or 0.0
        )

        ask = float(
            getattr(
                tick,
                "ask",
                0.0,
            )
            or 0.0
        )

        if bid <= 0 or ask <= 0:
            return False

        if position_type == mt5.POSITION_TYPE_BUY:

            order_type = (
                mt5.ORDER_TYPE_SELL
            )

            price = bid

        elif position_type == mt5.POSITION_TYPE_SELL:

            order_type = (
                mt5.ORDER_TYPE_BUY
            )

            price = ask

        else:

            logger.warning(
                "CLOSE POSITION: "
                "UNKNOWN TYPE=%s TICKET=%s",
                position_type,
                ticket,
            )

            return False

        normalized_price = normalize_price(
            symbol,
            price,
        )

        if normalized_price is None:

            logger.error(
                "CLOSE POSITION: "
                "PRICE NORMALIZATION FAILED "
                "SYMBOL=%s TICKET=%s",
                symbol,
                ticket,
            )

            return False

        info = get_symbol_info(
            symbol
        )

        if info is None:

            logger.warning(
                "CLOSE POSITION: "
                "SYMBOL INFO NOT FOUND "
                "SYMBOL=%s",
                symbol,
            )

            return False

        filling_mode = getattr(
            info,
            "filling_mode",
            mt5.ORDER_FILLING_FOK,
        )

        if not _live_trading_allowed():

            logger.critical(
                "CLOSE POSITION BLOCKED "
                "BY LIVE SAFETY GATE "
                "TICKET=%s SYMBOL=%s",
                ticket,
                symbol,
            )

            return False

        request = {
            "action":
                mt5.TRADE_ACTION_DEAL,

            "symbol":
                symbol,

            "volume":
                volume,

            "type":
                order_type,

            "position":
                int(ticket),

            "price":
                normalized_price,

            "deviation":
                DEVIATION,

            "magic":
                MAGIC_NUMBER,

            "comment":
                ORDER_COMMENT_CLOSE,

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode,
        }

        # ----------------------------------------------------
        # PRE-FLIGHT ORDER CHECK
        # ----------------------------------------------------

        if not _order_check(
            request,
            "CLOSE POSITION",
        ):

            return False

        logger.info(
            "CLOSE POSITION: SEND "
            "TICKET=%s SYMBOL=%s "
            "TYPE=%s VOLUME=%.2f "
            "BID=%.5f ASK=%.5f "
            "CLOSE_PRICE=%.5f",
            ticket,
            symbol,
            order_type,
            volume,
            bid,
            ask,
            normalized_price,
        )

        # ----------------------------------------------------
        # SINGLE SEND - NO BLIND RETRY
        # ----------------------------------------------------

        result = mt5.order_send(
            request
        )

        if result is None:

            logger.error(
                "CLOSE POSITION FAILED "
                "TICKET=%s ERROR=%s",
                ticket,
                mt5.last_error(),
            )

            return False

        retcode = int(
            getattr(
                result,
                "retcode",
                0,
            )
            or 0
        )

        if retcode not in (
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_DONE_PARTIAL,
        ):

            logger.error(
                "CLOSE POSITION REJECTED "
                "TICKET=%s RETCODE=%s COMMENT=%s",
                ticket,
                retcode,
                getattr(
                    result,
                    "comment",
                    "",
                ),
            )

            return False

        logger.info(
            "POSITION CLOSED SUCCESS "
            "TICKET=%s SYMBOL=%s "
            "RETCODE=%s",
            ticket,
            symbol,
            retcode,
        )

        return True

    except Exception as exc:

        logger.exception(
            "CLOSE POSITION ERROR "
            "TICKET=%s ERROR=%s",
            ticket,
            exc,
        )

        return False


# ============================================================
# AUTO SL / TP
# ============================================================

def manage_auto_sl_tp(
    position: Any,
) -> bool:

    try:

        if not _ensure_mt5():
            return False

        if not _validate_project_position(
            position
        ):
            return False

        ticket = _position_ticket(
            position
        )

        symbol = _position_symbol(
            position
        )

        position_type = _position_type(
            position
        )

        if ticket is None or not symbol:
            return False

        current_sl = _position_sl(
            position
        )

        current_tp = _position_tp(
            position
        )

        entry_price = _position_price_open(
            position
        )

        if entry_price <= 0:
            return False

        if (
            current_sl > 0
            and current_tp > 0
        ):

            return False

        atr = calculate_atr(
            symbol
        )

        if atr is None:

            logger.warning(
                "AUTO SLTP: "
                "ATR UNAVAILABLE "
                "TICKET=%s SYMBOL=%s",
                ticket,
                symbol,
            )

            return False

        calculated = calculate_atr_sl_tp(
            symbol=symbol,
            position_type=position_type,
            entry_price=entry_price,
            atr=atr,
        )

        if not calculated:
            return False

        new_sl = (
            current_sl
            if current_sl > 0
            else calculated["sl"]
        )

        new_tp = (
            current_tp
            if current_tp > 0
            else calculated["tp"]
        )

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=new_sl,
            tp=new_tp,
        ):

            logger.warning(
                "AUTO SLTP: "
                "FINAL VALUES INVALID "
                "TICKET=%s SL=%.5f TP=%.5f",
                ticket,
                new_sl,
                new_tp,
            )

            return False

        logger.info(
            "AUTO SLTP: "
            "TICKET=%s SYMBOL=%s ATR=%.5f "
            "SL=%.5f TP=%.5f",
            ticket,
            symbol,
            atr,
            new_sl,
            new_tp,
        )

        success = modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=new_tp,
        )

        if success:

            logger.info(
                "AUTO SLTP SUCCESS "
                "TICKET=%s",
                ticket,
            )

        return success

    except Exception as exc:

        logger.exception(
            "AUTO SLTP ERROR %s",
            exc,
        )

        return False


# ============================================================
# RESULT CHECK
# ============================================================

def check_position_result(
    ticket: int,
    symbol: str,
) -> bool:

    try:

        if not _is_pilot_symbol(symbol):
            return False

        if not _ensure_mt5():
            return False

        positions = mt5.positions_get(
            ticket=int(ticket)
        )

        if not positions:

            logger.info(
                "POSITION NO LONGER OPEN "
                "TICKET=%s SYMBOL=%s",
                ticket,
                symbol,
            )

            return False

        position = positions[0]

        if not _validate_project_position(
            position
        ):
            return False

        return True

    except Exception:

        return False


# ============================================================
# PROFIT %
# ============================================================

def calculate_profit_percent(
    position: Any,
) -> float:

    try:

        if not _validate_project_position(
            position
        ):
            return 0.0

        if not _ensure_mt5():
            return 0.0

        symbol = _position_symbol(
            position
        )

        position_type = _position_type(
            position
        )

        entry = _position_price_open(
            position
        )

        if not symbol or entry <= 0:
            return 0.0

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return 0.0

        bid = float(
            getattr(
                tick,
                "bid",
                0.0,
            )
            or 0.0
        )

        ask = float(
            getattr(
                tick,
                "ask",
                0.0,
            )
            or 0.0
        )

        if bid <= 0 or ask <= 0:
            return 0.0

        if position_type == mt5.POSITION_TYPE_BUY:

            current = bid

            movement = (
                current
                - entry
            )

        elif position_type == mt5.POSITION_TYPE_SELL:

            current = ask

            movement = (
                entry
                - current
            )

        else:

            return 0.0

        return (
            movement / entry
        ) * 100.0

    except Exception:

        return 0.0


# ============================================================
# BREAK EVEN
# ============================================================

def manage_break_even(
    position: Any,
) -> bool:

    try:

        if not _ensure_mt5():
            return False

        if not _validate_project_position(
            position
        ):
            return False

        ticket = _position_ticket(
            position
        )

        symbol = _position_symbol(
            position
        )

        position_type = _position_type(
            position
        )

        if ticket is None or not symbol:
            return False

        current_sl = _position_sl(
            position
        )

        entry = _position_price_open(
            position
        )

        if entry <= 0:
            return False

        profit_percent = (
            calculate_profit_percent(
                position
            )
        )

        if (
            profit_percent
            < BREAK_EVEN_TRIGGER_PERCENT
        ):

            return False

        offset = (
            entry
            * (
                BREAK_EVEN_OFFSET_PERCENT
                / 100.0
            )
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            new_sl = (
                entry
                + offset
            )

            if (
                current_sl >= new_sl
                and current_sl > 0
            ):

                return False

            tp = _position_tp(
                position
            )

        elif position_type == mt5.POSITION_TYPE_SELL:

            new_sl = (
                entry
                - offset
            )

            if (
                current_sl <= new_sl
                and current_sl > 0
            ):

                return False

            tp = _position_tp(
                position
            )

        else:

            return False

        new_sl = normalize_price(
            symbol,
            new_sl,
        )

        if new_sl is None:
            return False

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=new_sl,
            tp=tp,
        ):

            return False

        logger.info(
            "BREAK EVEN "
            "TICKET=%s SYMBOL=%s "
            "SL=%.5f PROFIT=%.2f%%",
            ticket,
            symbol,
            new_sl,
            profit_percent,
        )

        return modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=tp,
        )

    except Exception as exc:

        logger.exception(
            "BREAK EVEN ERROR %s",
            exc,
        )

        return False


# ============================================================
# TRAILING STOP
# ============================================================

def manage_trailing_stop(
    position: Any,
) -> bool:

    try:

        if not _ensure_mt5():
            return False

        if not _validate_project_position(
            position
        ):
            return False

        ticket = _position_ticket(
            position
        )

        symbol = _position_symbol(
            position
        )

        position_type = _position_type(
            position
        )

        if ticket is None or not symbol:
            return False

        profit_percent = (
            calculate_profit_percent(
                position
            )
        )

        if (
            profit_percent
            < TRAILING_START_PERCENT
        ):

            return False

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:
            return False

        bid = float(
            getattr(
                tick,
                "bid",
                0.0,
            )
            or 0.0
        )

        ask = float(
            getattr(
                tick,
                "ask",
                0.0,
            )
            or 0.0
        )

        if bid <= 0 or ask <= 0:
            return False

        entry = _position_price_open(
            position
        )

        current_sl = _position_sl(
            position
        )

        tp = _position_tp(
            position
        )

        if entry <= 0:
            return False

        distance = (
            entry
            * (
                TRAILING_DISTANCE_PERCENT
                / 100.0
            )
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            new_sl = (
                bid
                - distance
            )

            if (
                current_sl > 0
                and new_sl <= current_sl
            ):

                return False

            if new_sl <= entry:
                return False

        elif position_type == mt5.POSITION_TYPE_SELL:

            new_sl = (
                ask
                + distance
            )

            if (
                current_sl > 0
                and new_sl >= current_sl
            ):

                return False

            if new_sl >= entry:
                return False

        else:

            return False

        new_sl = normalize_price(
            symbol,
            new_sl,
        )

        if new_sl is None:
            return False

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=new_sl,
            tp=tp,
        ):

            return False

        logger.info(
            "TRAILING STOP "
            "TICKET=%s SYMBOL=%s "
            "SL=%.5f PROFIT=%.2f%%",
            ticket,
            symbol,
            new_sl,
            profit_percent,
        )

        return modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=tp,
        )

    except Exception as exc:

        logger.exception(
            "TRAILING STOP ERROR %s",
            exc,
        )

        return False


# ============================================================
# MAIN POSITION MONITOR
# ============================================================

def monitor_positions() -> List[Dict[str, Any]]:
    """
    Monitor ONLY Pourya Trader AI positions for XAUUSD.su.

    Manual / foreign / other-symbol positions are ignored.

    While PAPER_TRADING=True or ALLOW_LIVE_TRADING=False,
    the manager may analyze positions but cannot perform
    real MT5 modifications.
    """

    results: List[Dict[str, Any]] = []

    try:

        if not _ensure_mt5():

            logger.warning(
                "POSITION MANAGER: "
                "MT5 NOT CONNECTED"
            )

            return results

        positions = get_open_positions()

        if positions is None:
            positions = []

        if not positions:

            logger.info(
                "POSITION MANAGER: "
                "NO OPEN POSITIONS"
            )

            return results

        logger.info(
            "POSITION MANAGER: "
            "OPEN POSITIONS=%s",
            len(positions),
        )

        for position in positions:

            try:

                ticket = _position_ticket(
                    position
                )

                symbol = _position_symbol(
                    position
                )

                magic = _position_magic(
                    position
                )

                if ticket is None:

                    logger.warning(
                        "POSITION PROCESS: "
                        "INVALID TICKET"
                    )

                    continue

                # ------------------------------------------------
                # SYMBOL FILTER
                # ------------------------------------------------

                if not _is_pilot_symbol(symbol):

                    logger.info(
                        "POSITION MANAGER: "
                        "SKIP NON-PILOT POSITION "
                        "TICKET=%s SYMBOL=%s "
                        "PILOT=%s",
                        ticket,
                        symbol,
                        PILOT_SYMBOL,
                    )

                    continue

                # ------------------------------------------------
                # MAGIC FILTER
                # ------------------------------------------------

                if magic != MAGIC_NUMBER:

                    logger.info(
                        "POSITION MANAGER: "
                        "SKIP FOREIGN POSITION "
                        "TICKET=%s MAGIC=%s "
                        "EXPECTED=%s SYMBOL=%s",
                        ticket,
                        magic,
                        MAGIC_NUMBER,
                        symbol,
                    )

                    continue

                position_type = _position_type(
                    position
                )

                if position_type not in (
                    mt5.POSITION_TYPE_BUY,
                    mt5.POSITION_TYPE_SELL,
                ):

                    logger.warning(
                        "POSITION PROCESS: "
                        "UNKNOWN TYPE "
                        "TICKET=%s TYPE=%s",
                        ticket,
                        position_type,
                    )

                    continue

                current_sl = _position_sl(
                    position
                )

                current_tp = _position_tp(
                    position
                )

                logger.info(
                    "POSITION MANAGER: "
                    "PROCESS TICKET=%s SYMBOL=%s "
                    "MAGIC=%s TYPE=%s VOLUME=%.2f "
                    "SL=%.5f TP=%.5f",
                    ticket,
                    symbol,
                    magic,
                    position_type,
                    _position_volume(position),
                    current_sl,
                    current_tp,
                )

                action_result = {
                    "ticket":
                        ticket,

                    "symbol":
                        symbol,

                    "magic":
                        magic,

                    "auto_sl_tp":
                        False,

                    "break_even":
                        False,

                    "trailing":
                        False,
                }

                # ------------------------------------------------
                # AUTO SL / TP
                # ------------------------------------------------

                if ENABLE_AUTO_SL_TP:

                    action_result[
                        "auto_sl_tp"
                    ] = manage_auto_sl_tp(
                        position
                    )

                # ------------------------------------------------
                # REFRESH POSITION AFTER SL/TP CHANGE
                # ------------------------------------------------

                if action_result[
                    "auto_sl_tp"
                ]:

                    refreshed = (
                        _get_position_by_ticket(
                            ticket
                        )
                    )

                    if refreshed is not None:

                        position = refreshed

                # ------------------------------------------------
                # BREAK EVEN
                # ------------------------------------------------

                if ENABLE_BREAK_EVEN:

                    action_result[
                        "break_even"
                    ] = manage_break_even(
                        position
                    )

                # ------------------------------------------------
                # REFRESH AGAIN AFTER BREAK EVEN
                # ------------------------------------------------

                if action_result[
                    "break_even"
                ]:

                    refreshed = (
                        _get_position_by_ticket(
                            ticket
                        )
                    )

                    if refreshed is not None:

                        position = refreshed

                # ------------------------------------------------
                # TRAILING STOP
                # ------------------------------------------------

                if ENABLE_TRAILING_STOP:

                    action_result[
                        "trailing"
                    ] = manage_trailing_stop(
                        position
                    )

                results.append(
                    action_result
                )

            except Exception as exc:

                logger.exception(
                    "POSITION PROCESS ERROR %s",
                    exc,
                )

        return results

    except Exception as exc:

        logger.exception(
            "POSITION MANAGER ERROR %s",
            exc,
        )

        return results


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

def modify_position_sl(
    ticket: int,
    symbol: str,
    sl: float,
) -> bool:

    try:

        if not _ensure_mt5():
            return False

        if not _is_pilot_symbol(symbol):
            return False

        position = _get_position_by_ticket(
            ticket
        )

        if position is None:
            return False

        if not _validate_project_position(
            position
        ):
            return False

        tp = _position_tp(
            position
        )

        return modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=sl,
            tp=tp,
        )

    except Exception as exc:

        logger.exception(
            "MODIFY POSITION SL ERROR %s",
            exc,
        )

        return False


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "monitor_positions",
    "manage_auto_sl_tp",
    "manage_break_even",
    "manage_trailing_stop",
    "calculate_atr",
    "calculate_atr_sl_tp",
    "calculate_profit_percent",
    "modify_position_sl_tp",
    "modify_position_sl",
    "validate_sl_tp",
    "get_min_stop_distance",
    "check_position_result",
    "close_position",
    "is_buy_position",
    "is_sell_position",
]
