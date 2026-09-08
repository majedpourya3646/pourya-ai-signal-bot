# core/position_manager.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

import MetaTrader5 as mt5

from core.logger import logger
from core.mt5_connector import (
    get_open_positions,
    get_symbol_info,
    get_symbol_tick,
    get_rates,
    normalize_price,
    update_trade_status,
)


# ============================================================
# CONFIG
# ============================================================

MAGIC_NUMBER = 20260731
DEVIATION = 20

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


# ============================================================
# GENERIC HELPERS
# ============================================================

def _get_value(obj: Any, key: str, default: Any = None) -> Any:
    """
    Read a field from either:
      - MT5 TradePosition namedtuple/object
      - dict
      - regular Python object
    """

    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(key, default)

    try:
        return getattr(obj, key)
    except AttributeError:
        return default


def _position_ticket(position: Any) -> Optional[int]:
    value = _get_value(position, "ticket")

    if value is None:
        return None

    try:
        return int(value)
    except Exception:
        return None


def _position_magic(position: Any) -> Optional[int]:
    value = _get_value(position, "magic")

    if value is None:
        return None

    try:
        return int(value)
    except Exception:
        return None


def _position_symbol(position: Any) -> Optional[str]:
    value = _get_value(position, "symbol")

    if value is None:
        return None

    return str(value)


def _position_type(position: Any) -> Optional[int]:
    value = _get_value(position, "type")

    if value is None:
        return None

    try:
        return int(value)
    except Exception:
        return None


def _position_volume(position: Any) -> float:
    value = _get_value(position, "volume", 0.0)

    try:
        return float(value)
    except Exception:
        return 0.0


def _position_price_open(position: Any) -> float:
    value = _get_value(position, "price_open", 0.0)

    try:
        return float(value)
    except Exception:
        return 0.0


def _position_sl(position: Any) -> float:
    value = _get_value(position, "sl", 0.0)

    try:
        return float(value)
    except Exception:
        return 0.0


def _position_tp(position: Any) -> float:
    value = _get_value(position, "tp", 0.0)

    try:
        return float(value)
    except Exception:
        return 0.0


def _is_buy_position(position: Any) -> bool:
    return _position_type(position) == mt5.POSITION_TYPE_BUY


def _is_sell_position(position: Any) -> bool:
    return _position_type(position) == mt5.POSITION_TYPE_SELL


# Public compatibility helpers
def is_buy_position(position: Any) -> bool:
    return _is_buy_position(position)


def is_sell_position(position: Any) -> bool:
    return _is_sell_position(position)


# ============================================================
# ATR
# ============================================================

def calculate_atr(
    symbol: str,
    timeframe: int = ATR_TIMEFRAME,
    period: int = ATR_PERIOD,
) -> Optional[float]:
    """
    Calculate simple ATR from MT5 OHLC data.
    """

    try:
        if not mt5.terminal_info():
            logger.warning("ATR: MT5 TERMINAL NOT CONNECTED")
            return None

        bars_needed = max(period + 5, 30)

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
                "ATR: NOT ENOUGH DATA SYMBOL=%s COUNT=%s REQUIRED=%s",
                symbol,
                len(rates),
                period + 1,
            )
            return None

        true_ranges: List[float] = []

        for i in range(1, len(rates)):
            current = rates[i]
            previous = rates[i - 1]

            high = float(current["high"])
            low = float(current["low"])
            previous_close = float(previous["close"])

            tr = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )

            true_ranges.append(tr)

        if len(true_ranges) < period:
            return None

        recent_tr = true_ranges[-period:]

        atr = sum(recent_tr) / len(recent_tr)

        if atr <= 0:
            return None

        return float(atr)

    except Exception as exc:
        logger.exception("ATR CALCULATION ERROR %s", exc)
        return None


# ============================================================
# BROKER STOP DISTANCE
# ============================================================

def get_min_stop_distance(symbol: str) -> float:
    """
    Return broker minimum stop distance in price units.
    """

    try:
        info = get_symbol_info(symbol)

        if info is None:
            return 0.0

        point = float(getattr(info, "point", 0.0) or 0.0)

        stops_level = int(
            getattr(info, "trade_stops_level", 0) or 0
        )

        freeze_level = int(
            getattr(info, "trade_freeze_level", 0) or 0
        )

        level = max(stops_level, freeze_level)

        if point <= 0 or level <= 0:
            return 0.0

        return level * point

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
    """
    Validate SL/TP against current market price and broker limits.
    """

    try:
        tick = get_symbol_tick(symbol)

        if tick is None:
            return False

        bid = float(getattr(tick, "bid", 0.0) or 0.0)
        ask = float(getattr(tick, "ask", 0.0) or 0.0)

        if bid <= 0 or ask <= 0:
            return False

        min_distance = get_min_stop_distance(symbol)

        if position_type == mt5.POSITION_TYPE_BUY:
            reference_price = bid

            if sl >= reference_price:
                return False

            if tp <= reference_price:
                return False

            if min_distance > 0:
                if (reference_price - sl) < min_distance:
                    return False

                if (tp - reference_price) < min_distance:
                    return False

            return True

        if position_type == mt5.POSITION_TYPE_SELL:
            reference_price = ask

            if sl <= reference_price:
                return False

            if tp >= reference_price:
                return False

            if min_distance > 0:
                if (sl - reference_price) < min_distance:
                    return False

                if (reference_price - tp) < min_distance:
                    return False

            return True

        return False

    except Exception as exc:
        logger.exception(
            "SL TP VALIDATION ERROR SYMBOL=%s ERROR=%s",
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
    """
    Calculate ATR based SL/TP.
    """

    try:
        if entry_price <= 0:
            return None

        if atr is None:
            atr = calculate_atr(symbol)

        if atr is None or atr <= 0:
            return None

        sl_distance = atr * ATR_SL_MULTIPLIER
        tp_distance = atr * ATR_TP_MULTIPLIER

        if position_type == mt5.POSITION_TYPE_BUY:
            sl = entry_price - sl_distance
            tp = entry_price + tp_distance

        elif position_type == mt5.POSITION_TYPE_SELL:
            sl = entry_price + sl_distance
            tp = entry_price - tp_distance

        else:
            return None

        sl = normalize_price(symbol, sl)
        tp = normalize_price(symbol, tp)

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=sl,
            tp=tp,
        ):
            logger.warning(
                "ATR SL/TP INVALID SYMBOL=%s TYPE=%s SL=%.5f TP=%.5f",
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
            "sl_distance": float(sl_distance),
            "tp_distance": float(tp_distance),
        }

    except Exception as exc:
        logger.exception(
            "ATR SL TP CALCULATION ERROR SYMBOL=%s ERROR=%s",
            symbol,
            exc,
        )
        return None


# ============================================================
# MODIFY POSITION SL / TP
# ============================================================

def modify_position_sl_tp(
    ticket: int,
    symbol: str,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
) -> bool:
    """
    Modify an existing position's SL/TP using TRADE_ACTION_SLTP.
    """

    try:
        if not mt5.terminal_info():
            logger.warning(
                "MODIFY SLTP: MT5 NOT CONNECTED"
            )
            return False

        positions = mt5.positions_get(ticket=int(ticket))

        if not positions:
            logger.warning(
                "MODIFY SLTP: POSITION NOT FOUND TICKET=%s",
                ticket,
            )
            return False

        position = positions[0]

        current_sl = float(
            getattr(position, "sl", 0.0) or 0.0
        )

        current_tp = float(
            getattr(position, "tp", 0.0) or 0.0
        )

        if sl is None:
            sl = current_sl

        if tp is None:
            tp = current_tp

        sl = float(sl or 0.0)
        tp = float(tp or 0.0)

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": int(ticket),
            "symbol": symbol,
            "sl": sl,
            "tp": tp,
            "magic": MAGIC_NUMBER,
            "comment": "Pourya AI SLTP",
        }

        result = mt5.order_send(request)

        if result is None:
            logger.error(
                "MODIFY SLTP FAILED TICKET=%s ERROR=%s",
                ticket,
                mt5.last_error(),
            )
            return False

        retcode = int(
            getattr(result, "retcode", 0) or 0
        )

        if retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(
                "MODIFY SLTP REJECTED TICKET=%s RETCODE=%s COMMENT=%s",
                ticket,
                retcode,
                getattr(result, "comment", ""),
            )
            return False

        logger.info(
            "SL/TP UPDATED TICKET=%s SYMBOL=%s SL=%.5f TP=%.5f RETCODE=%s",
            ticket,
            symbol,
            sl,
            tp,
            retcode,
        )

        return True

    except Exception as exc:
        logger.exception(
            "MODIFY SLTP ERROR TICKET=%s ERROR=%s",
            ticket,
            exc,
        )
        return False


# ============================================================
# AUTO SL / TP
# ============================================================

def manage_auto_sl_tp(position: Any) -> bool:
    """
    Add ATR based SL/TP only when they are missing.

    Existing SL/TP are never overwritten.
    """

    try:
        ticket = _position_ticket(position)
        symbol = _position_symbol(position)
        position_type = _position_type(position)

        if ticket is None or not symbol:
            return False

        if position_type not in (
            mt5.POSITION_TYPE_BUY,
            mt5.POSITION_TYPE_SELL,
        ):
            return False

        current_sl = _position_sl(position)
        current_tp = _position_tp(position)
        entry_price = _position_price_open(position)

        if entry_price <= 0:
            logger.warning(
                "AUTO SLTP: INVALID ENTRY TICKET=%s",
                ticket,
            )
            return False

        # Nothing missing.
        if current_sl > 0 and current_tp > 0:
            return False

        atr = calculate_atr(symbol)

        if atr is None:
            logger.warning(
                "AUTO SLTP: ATR UNAVAILABLE TICKET=%s SYMBOL=%s",
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

        # Validate complete pair.
        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=new_sl,
            tp=new_tp,
        ):
            logger.warning(
                "AUTO SLTP: FINAL VALUES INVALID "
                "TICKET=%s SL=%.5f TP=%.5f",
                ticket,
                new_sl,
                new_tp,
            )
            return False

        logger.info(
            "AUTO SLTP: TICKET=%s SYMBOL=%s ATR=%.5f SL=%.5f TP=%.5f",
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
                "AUTO SLTP SUCCESS TICKET=%s",
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
    """
    Check whether a position still exists.
    """

    try:
        positions = mt5.positions_get(ticket=int(ticket))

        if not positions:
            logger.info(
                "POSITION NO LONGER OPEN TICKET=%s SYMBOL=%s",
                ticket,
                symbol,
            )
            return False

        return True

    except Exception:
        return False


# ============================================================
# PROFIT %
# ============================================================

def calculate_profit_percent(position: Any) -> float:
    """
    Calculate price movement percentage relative to entry.
    """

    try:
        symbol = _position_symbol(position)
        position_type = _position_type(position)
        entry = _position_price_open(position)

        if not symbol or entry <= 0:
            return 0.0

        tick = get_symbol_tick(symbol)

        if tick is None:
            return 0.0

        bid = float(getattr(tick, "bid", 0.0) or 0.0)
        ask = float(getattr(tick, "ask", 0.0) or 0.0)

        if bid <= 0 or ask <= 0:
            return 0.0

        if position_type == mt5.POSITION_TYPE_BUY:
            current = bid
            movement = current - entry

        elif position_type == mt5.POSITION_TYPE_SELL:
            current = ask
            movement = entry - current

        else:
            return 0.0

        return (movement / entry) * 100.0

    except Exception:
        return 0.0


# ============================================================
# BREAK EVEN
# ============================================================

def manage_break_even(position: Any) -> bool:
    """
    Move SL toward/above entry after profit threshold.
    """

    try:
        ticket = _position_ticket(position)
        symbol = _position_symbol(position)
        position_type = _position_type(position)

        if ticket is None or not symbol:
            return False

        current_sl = _position_sl(position)
        entry = _position_price_open(position)

        if entry <= 0:
            return False

        profit_percent = calculate_profit_percent(position)

        if profit_percent < BREAK_EVEN_TRIGGER_PERCENT:
            return False

        offset = entry * (
            BREAK_EVEN_OFFSET_PERCENT / 100.0
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            new_sl = entry + offset

            if current_sl >= new_sl and current_sl > 0:
                return False

            tp = _position_tp(position)

        elif position_type == mt5.POSITION_TYPE_SELL:

            new_sl = entry - offset

            if current_sl <= new_sl and current_sl > 0:
                return False

            tp = _position_tp(position)

        else:
            return False

        new_sl = normalize_price(symbol, new_sl)

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=new_sl,
            tp=tp,
        ):
            return False

        logger.info(
            "BREAK EVEN TICKET=%s SYMBOL=%s SL=%.5f PROFIT=%.2f%%",
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

def manage_trailing_stop(position: Any) -> bool:
    """
    Apply trailing stop after the configured profit threshold.
    """

    try:
        ticket = _position_ticket(position)
        symbol = _position_symbol(position)
        position_type = _position_type(position)

        if ticket is None or not symbol:
            return False

        profit_percent = calculate_profit_percent(position)

        if profit_percent < TRAILING_START_PERCENT:
            return False

        tick = get_symbol_tick(symbol)

        if tick is None:
            return False

        bid = float(getattr(tick, "bid", 0.0) or 0.0)
        ask = float(getattr(tick, "ask", 0.0) or 0.0)

        if bid <= 0 or ask <= 0:
            return False

        entry = _position_price_open(position)
        current_sl = _position_sl(position)
        tp = _position_tp(position)

        if entry <= 0:
            return False

        distance = entry * (
            TRAILING_DISTANCE_PERCENT / 100.0
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            new_sl = bid - distance

            if current_sl > 0 and new_sl <= current_sl:
                return False

            if new_sl <= entry:
                return False

        elif position_type == mt5.POSITION_TYPE_SELL:

            new_sl = ask + distance

            if current_sl > 0 and new_sl >= current_sl:
                return False

            if new_sl >= entry:
                return False

        else:
            return False

        new_sl = normalize_price(symbol, new_sl)

        if not validate_sl_tp(
            symbol=symbol,
            position_type=position_type,
            sl=new_sl,
            tp=tp,
        ):
            return False

        logger.info(
            "TRAILING STOP TICKET=%s SYMBOL=%s SL=%.5f PROFIT=%.2f%%",
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
    Monitor ONLY positions belonging to Pourya Trader AI.

    Manual / foreign positions are ignored.

    This function supports both:
      - MT5 TradePosition objects
      - dictionaries
    """

    results: List[Dict[str, Any]] = []

    try:
        terminal = mt5.terminal_info()

        if terminal is None:
            logger.warning(
                "POSITION MANAGER: MT5 NOT CONNECTED"
            )
            return results

        positions = get_open_positions()

        if positions is None:
            positions = []

        if not positions:
            logger.info(
                "POSITION MANAGER: NO OPEN POSITIONS"
            )
            return results

        logger.info(
            "POSITION MANAGER: OPEN POSITIONS=%s",
            len(positions),
        )

        for position in positions:

            try:
                ticket = _position_ticket(position)
                symbol = _position_symbol(position)
                magic = _position_magic(position)

                if ticket is None:
                    logger.warning(
                        "POSITION PROCESS: INVALID TICKET"
                    )
                    continue

                # ------------------------------------------------
                # CRITICAL SAFETY FILTER
                # ------------------------------------------------
                # Manual / foreign trades must NEVER be modified.
                # ------------------------------------------------

                if magic is None:
                    logger.info(
                        "POSITION MANAGER: "
                        "SKIP FOREIGN POSITION "
                        "TICKET=%s MAGIC=None SYMBOL=%s",
                        ticket,
                        symbol,
                    )
                    continue

                if magic != MAGIC_NUMBER:
                    logger.info(
                        "POSITION MANAGER: "
                        "SKIP FOREIGN POSITION "
                        "TICKET=%s MAGIC=%s EXPECTED=%s SYMBOL=%s",
                        ticket,
                        magic,
                        MAGIC_NUMBER,
                        symbol,
                    )
                    continue

                if not symbol:
                    logger.warning(
                        "POSITION PROCESS: SYMBOL MISSING TICKET=%s",
                        ticket,
                    )
                    continue

                position_type = _position_type(position)

                if position_type not in (
                    mt5.POSITION_TYPE_BUY,
                    mt5.POSITION_TYPE_SELL,
                ):
                    logger.warning(
                        "POSITION PROCESS: "
                        "UNKNOWN TYPE TICKET=%s TYPE=%s",
                        ticket,
                        position_type,
                    )
                    continue

                current_sl = _position_sl(position)
                current_tp = _position_tp(position)

                logger.info(
                    "POSITION MANAGER: "
                    "PROCESS TICKET=%s SYMBOL=%s MAGIC=%s "
                    "TYPE=%s VOLUME=%.2f SL=%.5f TP=%.5f",
                    ticket,
                    symbol,
                    magic,
                    position_type,
                    _position_volume(position),
                    current_sl,
                    current_tp,
                )

                action_result = {
                    "ticket": ticket,
                    "symbol": symbol,
                    "magic": magic,
                    "auto_sl_tp": False,
                    "break_even": False,
                    "trailing": False,
                }

                # ------------------------------------------------
                # AUTO SL / TP
                # ------------------------------------------------

                if ENABLE_AUTO_SL_TP:
                    action_result["auto_sl_tp"] = (
                        manage_auto_sl_tp(position)
                    )

                # ------------------------------------------------
                # BREAK EVEN
                # ------------------------------------------------

                if ENABLE_BREAK_EVEN:
                    action_result["break_even"] = (
                        manage_break_even(position)
                    )

                # ------------------------------------------------
                # TRAILING STOP
                # ------------------------------------------------

                if ENABLE_TRAILING_STOP:
                    action_result["trailing"] = (
                        manage_trailing_stop(position)
                    )

                results.append(action_result)

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
    """
    Backward-compatible helper.
    Keeps existing TP unchanged.
    """

    try:
        positions = mt5.positions_get(ticket=int(ticket))

        if not positions:
            return False

        position = positions[0]

        tp = float(
            getattr(position, "tp", 0.0) or 0.0
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
    "is_buy_position",
    "is_sell_position",
]
