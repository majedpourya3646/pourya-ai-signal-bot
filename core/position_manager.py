# core/position_manager.py

from typing import Optional, Dict, Any, List

import MetaTrader5 as mt5

from core.logger import logger

from core.trade_manager import (
    update_trade_status
)

from core.mt5_connector import (
    is_connected,
    get_open_positions,
    get_symbol_tick,
    get_symbol_info,
    normalize_price,
    get_filling_mode
)


# ============================================================
# Configuration
# ============================================================

MAGIC_NUMBER = 20260731

DEVIATION = 20


# ============================================================
# Automatic ATR SL / TP
# ============================================================

ENABLE_AUTO_SL_TP = True

ATR_TIMEFRAME = mt5.TIMEFRAME_M15

ATR_PERIOD = 14

ATR_SL_MULTIPLIER = 1.5

ATR_TP_MULTIPLIER = 3.0


# ============================================================
# Break Even
# ============================================================

ENABLE_BREAK_EVEN = True

BREAK_EVEN_TRIGGER_PERCENT = 1.0

BREAK_EVEN_OFFSET_PERCENT = 0.05


# ============================================================
# Trailing Stop
# ============================================================

ENABLE_TRAILING_STOP = True

TRAILING_START_PERCENT = 1.5

TRAILING_DISTANCE_PERCENT = 0.75


# ============================================================
# Helpers
# ============================================================

def is_buy_position(
    position: Dict[str, Any]
) -> bool:

    return (
        position.get("type")
        == mt5.POSITION_TYPE_BUY
    )


def is_sell_position(
    position: Dict[str, Any]
) -> bool:

    return (
        position.get("type")
        == mt5.POSITION_TYPE_SELL
    )


# ============================================================
# ATR
# ============================================================

def calculate_atr(
    symbol: str,
    timeframe: int = ATR_TIMEFRAME,
    period: int = ATR_PERIOD
) -> Optional[float]:

    try:

        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            period + 20
        )

        if rates is None:

            logger.warning(
                f"ATR DATA FAILED SYMBOL={symbol} "
                f"ERROR={mt5.last_error()}"
            )

            return None

        if len(rates) < period + 2:

            logger.warning(
                f"ATR NOT ENOUGH DATA "
                f"SYMBOL={symbol} "
                f"BARS={len(rates)}"
            )

            return None

        true_ranges = []

        for index in range(
            1,
            len(rates)
        ):

            high = float(
                rates[index]["high"]
            )

            low = float(
                rates[index]["low"]
            )

            previous_close = float(
                rates[index - 1]["close"]
            )

            tr1 = high - low

            tr2 = abs(
                high - previous_close
            )

            tr3 = abs(
                low - previous_close
            )

            true_range = max(
                tr1,
                tr2,
                tr3
            )

            true_ranges.append(
                true_range
            )

        if len(true_ranges) < period:

            return None

        atr = (
            sum(
                true_ranges[-period:]
            )
            / period
        )

        if atr <= 0:

            return None

        return float(atr)

    except Exception as exc:

        logger.exception(
            f"ATR CALCULATION ERROR {exc}"
        )

        return None


# ============================================================
# Broker Stop Distance
# ============================================================

def get_min_stop_distance(
    symbol: str
) -> float:

    try:

        info = get_symbol_info(
            symbol
        )

        if info is None:

            return 0.0

        point = float(
            getattr(
                info,
                "point",
                0.0
            )
        )

        stops_level = int(
            getattr(
                info,
                "trade_stops_level",
                0
            )
        )

        freeze_level = int(
            getattr(
                info,
                "trade_freeze_level",
                0
            )
        )

        level = max(
            stops_level,
            freeze_level
        )

        return float(
            level * point
        )

    except Exception as exc:

        logger.error(
            f"STOP DISTANCE ERROR {exc}"
        )

        return 0.0


# ============================================================
# Validate SL / TP
# ============================================================

def validate_sl_tp(
    symbol: str,
    position_type: int,
    sl: Optional[float],
    tp: Optional[float]
) -> bool:

    try:

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            return False

        bid = float(
            tick.bid
        )

        ask = float(
            tick.ask
        )

        minimum_distance = (
            get_min_stop_distance(
                symbol
            )
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            if sl is not None:

                if sl >= (
                    bid - minimum_distance
                ):

                    return False

            if tp is not None:

                if tp <= (
                    bid + minimum_distance
                ):

                    return False

            return True

        if position_type == mt5.POSITION_TYPE_SELL:

            if sl is not None:

                if sl <= (
                    ask + minimum_distance
                ):

                    return False

            if tp is not None:

                if tp >= (
                    ask - minimum_distance
                ):

                    return False

            return True

        return False

    except Exception as exc:

        logger.error(
            f"SL TP VALIDATION ERROR {exc}"
        )

        return False


# ============================================================
# Calculate ATR SL / TP
# ============================================================

def calculate_atr_sl_tp(
    position: Dict[str, Any],
    atr: float
):

    try:

        symbol = position.get(
            "symbol"
        )

        position_type = position.get(
            "type"
        )

        entry = float(
            position.get(
                "price_open",
                0
            )
        )

        if not symbol or entry <= 0:

            return None, None

        info = get_symbol_info(
            symbol
        )

        if info is None:

            return None, None

        sl_distance = (
            atr
            * ATR_SL_MULTIPLIER
        )

        tp_distance = (
            atr
            * ATR_TP_MULTIPLIER
        )

        if position_type == mt5.POSITION_TYPE_BUY:

            sl = entry - sl_distance

            tp = entry + tp_distance

        elif position_type == mt5.POSITION_TYPE_SELL:

            sl = entry + sl_distance

            tp = entry - tp_distance

        else:

            return None, None

        sl = normalize_price(
            symbol,
            sl
        )

        tp = normalize_price(
            symbol,
            tp
        )

        if sl is None or tp is None:

            return None, None

        return sl, tp

    except Exception as exc:

        logger.exception(
            f"ATR SL TP CALCULATION ERROR {exc}"
        )

        return None, None


# ============================================================
# Modify Position SL / TP
# ============================================================

def modify_position_sl_tp(
    ticket: int,
    symbol: str,
    sl: Optional[float],
    tp: Optional[float]
) -> bool:

    try:

        if not is_connected():

            logger.warning(
                "MODIFY SL TP: MT5 NOT CONNECTED"
            )

            return False

        request = {

            "action":
                mt5.TRADE_ACTION_SLTP,

            "symbol":
                symbol,

            "position":
                int(ticket),

            "sl":
                float(sl) if sl else 0.0,

            "tp":
                float(tp) if tp else 0.0,

        }

        result = mt5.order_send(
            request
        )

        if result is None:

            logger.error(
                f"MODIFY SL TP FAILED "
                f"TICKET={ticket} "
                f"ERROR={mt5.last_error()}"
            )

            return False

        logger.info(
            f"MODIFY SL TP RESULT "
            f"TICKET={ticket} "
            f"RETCODE={result.retcode} "
            f"COMMENT={result.comment}"
        )

        if result.retcode == (
            mt5.TRADE_RETCODE_DONE
        ):

            return True

        return False

    except Exception as exc:

        logger.exception(
            f"MODIFY SL TP ERROR {exc}"
        )

        return False


# ============================================================
# Auto SL / TP
# ============================================================

def manage_auto_sl_tp(
    position: Dict[str, Any]
) -> bool:

    try:

        ticket = position.get(
            "ticket"
        )

        symbol = position.get(
            "symbol"
        )

        current_sl = float(
            position.get(
                "sl",
                0
            ) or 0
        )

        current_tp = float(
            position.get(
                "tp",
                0
            ) or 0
        )

        if not ticket or not symbol:

            return False

        # ----------------------------------------------------
        # If both already exist, do nothing
        # ----------------------------------------------------

        if (
            current_sl > 0
            and current_tp > 0
        ):

            return False

        atr = calculate_atr(
            symbol=symbol,
            timeframe=ATR_TIMEFRAME,
            period=ATR_PERIOD
        )

        if atr is None:

            return False

        sl, tp = calculate_atr_sl_tp(
            position,
            atr
        )

        if sl is None or tp is None:

            return False

        position_type = position.get(
            "type"
        )

        if not validate_sl_tp(
            symbol,
            position_type,
            sl,
            tp
        ):

            logger.warning(
                f"AUTO SL TP INVALID "
                f"TICKET={ticket} "
                f"SL={sl} "
                f"TP={tp}"
            )

            return False

        logger.info(
            f"AUTO SL TP "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"ATR={atr:.4f} "
            f"SL={sl} "
            f"TP={tp}"
        )

        return modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=sl,
            tp=tp
        )

    except Exception as exc:

        logger.exception(
            f"AUTO SL TP ERROR {exc}"
        )

        return False


# ============================================================
# Database Position Result
# ============================================================

def check_position_result(
    position: Dict[str, Any]
):

    try:

        ticket = position.get(
            "ticket"
        )

        profit = float(
            position.get(
                "profit",
                0
            ) or 0
        )

        if ticket is None:

            return

        if profit > 0:

            update_trade_status(
                ticket,
                "PROFIT"
            )

        elif profit < 0:

            update_trade_status(
                ticket,
                "LOSS"
            )

        else:

            update_trade_status(
                ticket,
                "OPEN"
            )

    except Exception as exc:

        logger.error(
            f"CHECK POSITION ERROR {exc}"
        )


# ============================================================
# Profit Percent
# ============================================================

def calculate_profit_percent(
    position: Dict[str, Any]
) -> float:

    try:

        entry = float(
            position.get(
                "price_open",
                0
            )
        )

        current = float(
            position.get(
                "price_current",
                0
            )
        )

        position_type = position.get(
            "type"
        )

        if entry <= 0:

            return 0.0

        if position_type == (
            mt5.POSITION_TYPE_BUY
        ):

            result = (
                (
                    current - entry
                )
                / entry
            ) * 100

        elif position_type == (
            mt5.POSITION_TYPE_SELL
        ):

            result = (
                (
                    entry - current
                )
                / entry
            ) * 100

        else:

            return 0.0

        return float(result)

    except Exception as exc:

        logger.error(
            f"PROFIT PERCENT ERROR {exc}"
        )

        return 0.0


# ============================================================
# Break Even
# ============================================================

def manage_break_even(
    position: Dict[str, Any]
) -> bool:

    try:

        ticket = position.get(
            "ticket"
        )

        symbol = position.get(
            "symbol"
        )

        entry = float(
            position.get(
                "price_open",
                0
            )
        )

        current_sl = float(
            position.get(
                "sl",
                0
            ) or 0
        )

        current_tp = position.get(
            "tp"
        )

        if not ticket or not symbol:

            return False

        if entry <= 0:

            return False

        profit_percent = (
            calculate_profit_percent(
                position
            )
        )

        if profit_percent < (
            BREAK_EVEN_TRIGGER_PERCENT
        ):

            return False

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if is_buy_position(position):

            if (
                current_sl > 0
                and current_sl >= entry
            ):

                return False

            new_sl = (
                entry
                * (
                    1
                    + (
                        BREAK_EVEN_OFFSET_PERCENT
                        / 100
                    )
                )
            )

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        elif is_sell_position(position):

            if (
                current_sl > 0
                and current_sl <= entry
            ):

                return False

            new_sl = (
                entry
                * (
                    1
                    - (
                        BREAK_EVEN_OFFSET_PERCENT
                        / 100
                    )
                )
            )

        else:

            return False

        new_sl = normalize_price(
            symbol,
            new_sl
        )

        if new_sl is None:

            return False

        if not validate_sl_tp(
            symbol,
            position.get("type"),
            new_sl,
            None
        ):

            logger.warning(
                f"BREAK EVEN INVALID "
                f"TICKET={ticket} "
                f"SL={new_sl}"
            )

            return False

        logger.info(
            f"BREAK EVEN "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"PROFIT={profit_percent:.2f}% "
            f"NEW_SL={new_sl}"
        )

        return modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=current_tp
        )

    except Exception as exc:

        logger.exception(
            f"BREAK EVEN ERROR {exc}"
        )

        return False


# ============================================================
# Trailing Stop
# ============================================================

def manage_trailing_stop(
    position: Dict[str, Any]
) -> bool:

    try:

        ticket = position.get(
            "ticket"
        )

        symbol = position.get(
            "symbol"
        )

        current = float(
            position.get(
                "price_current",
                0
            )
        )

        current_sl = float(
            position.get(
                "sl",
                0
            ) or 0
        )

        current_tp = position.get(
            "tp"
        )

        if not ticket or not symbol:

            return False

        if current <= 0:

            return False

        profit_percent = (
            calculate_profit_percent(
                position
            )
        )

        if profit_percent < (
            TRAILING_START_PERCENT
        ):

            return False

        distance = (
            current
            * (
                TRAILING_DISTANCE_PERCENT
                / 100
            )
        )

        if is_buy_position(position):

            new_sl = current - distance

            if (
                current_sl > 0
                and new_sl <= current_sl
            ):

                return False

        elif is_sell_position(position):

            new_sl = current + distance

            if (
                current_sl > 0
                and new_sl >= current_sl
            ):

                return False

        else:

            return False

        new_sl = normalize_price(
            symbol,
            new_sl
        )

        if new_sl is None:

            return False

        if not validate_sl_tp(
            symbol,
            position.get("type"),
            new_sl,
            None
        ):

            return False

        logger.info(
            f"TRAILING STOP "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"PROFIT={profit_percent:.2f}% "
            f"OLD_SL={current_sl} "
            f"NEW_SL={new_sl}"
        )

        return modify_position_sl_tp(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=current_tp
        )

    except Exception as exc:

        logger.exception(
            f"TRAILING STOP ERROR {exc}"
        )

        return False


# ============================================================
# Monitor Positions
# ============================================================

def monitor_positions() -> List[Dict[str, Any]]:

    try:

        if not is_connected():

            logger.warning(
                "POSITION MANAGER: MT5 NOT CONNECTED"
            )

            return []

        positions = get_open_positions()

        if not positions:

            logger.info(
                "NO OPEN POSITIONS"
            )

            return []

        active = []

        for position in positions:

            try:

                magic = position.get(
                    "magic"
                )

                # ------------------------------------------------
                # IMPORTANT:
                # Only Pourya Trader AI positions
                # ------------------------------------------------

                if magic is None:

                    logger.info(
                        f"SKIP FOREIGN POSITION "
                        f"TICKET={position.get('ticket')} "
                        f"MAGIC=None"
                    )

                    continue

                if int(magic) != MAGIC_NUMBER:

                    logger.info(
                        f"SKIP FOREIGN POSITION "
                        f"TICKET={position.get('ticket')} "
                        f"MAGIC={magic}"
                    )

                    continue

                data = {

                    "ticket":
                        position.get("ticket"),

                    "symbol":
                        position.get("symbol"),

                    "type":
                        position.get("type"),

                    "volume":
                        position.get("volume"),

                    "price_open":
                        position.get("price_open"),

                    "price_current":
                        position.get("price_current"),

                    "sl":
                        position.get("sl"),

                    "tp":
                        position.get("tp"),

                    "profit":
                        position.get("profit"),

                    "magic":
                        magic

                }

                active.append(
                    data
                )

                logger.info(
                    "POSITION "
                    f"TICKET={data['ticket']} "
                    f"SYMBOL={data['symbol']} "
                    f"VOLUME={data['volume']} "
                    f"OPEN={data['price_open']} "
                    f"CURRENT={data['price_current']} "
                    f"SL={data['sl']} "
                    f"TP={data['tp']} "
                    f"PROFIT={data['profit']}"
                )

                # ------------------------------------------------
                # Database
                # ------------------------------------------------

                check_position_result(
                    data
                )

                # ------------------------------------------------
                # Auto SL / TP
                # ------------------------------------------------

                if ENABLE_AUTO_SL_TP:

                    manage_auto_sl_tp(
                        data
                    )

                # ------------------------------------------------
                # Break Even
                # ------------------------------------------------

                if ENABLE_BREAK_EVEN:

                    manage_break_even(
                        data
                    )

                # ------------------------------------------------
                # Trailing Stop
                # ------------------------------------------------

                if ENABLE_TRAILING_STOP:

                    manage_trailing_stop(
                        data
                    )

            except Exception as exc:

                logger.exception(
                    f"POSITION PROCESS ERROR {exc}"
                )

        return active

    except Exception as exc:

        logger.exception(
            f"POSITION MONITOR ERROR {exc}"
        )

        return []


# ============================================================
# Compatibility Alias
# ============================================================

def modify_position_sl(
    ticket: int,
    symbol: str,
    sl: Optional[float],
    tp: Optional[float] = None
) -> bool:

    return modify_position_sl_tp(
        ticket=ticket,
        symbol=symbol,
        sl=sl,
        tp=tp
    )


# ============================================================
# End of File
# ============================================================
