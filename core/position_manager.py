# core/position_manager.py

from typing import Optional, Dict, Any, List

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

import MetaTrader5 as mt5


# ============================================================
# Configuration
# ============================================================

MAGIC_NUMBER = 20260731

DEVIATION = 20

# ------------------------------------------------------------
# Position management
# ------------------------------------------------------------

ENABLE_BREAK_EVEN = True

ENABLE_TRAILING_STOP = True

# Move SL to entry after this amount of profit.
# This is currently expressed as a percentage of entry price.
BREAK_EVEN_TRIGGER_PERCENT = 1.0

# Small protection above/below entry.
BREAK_EVEN_OFFSET_PERCENT = 0.05

# Start trailing after this profit.
TRAILING_START_PERCENT = 1.5

# Distance of trailing stop from current price.
TRAILING_DISTANCE_PERCENT = 0.75


# ============================================================
# MT5 Position Type Helpers
# ============================================================

def is_buy_position(position) -> bool:

    return position.type == mt5.POSITION_TYPE_BUY


def is_sell_position(position) -> bool:

    return position.type == mt5.POSITION_TYPE_SELL


# ============================================================
# Monitor Positions
# ============================================================

def monitor_positions() -> List[Dict[str, Any]]:
    """
    Read all open MT5 positions and manage them.

    Responsibilities:

    - Detect open positions
    - Log current state
    - Update trade status
    - Manage break-even
    - Manage trailing stop
    """

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
                        position.get("magic")

                }

                active.append(data)

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

                # ----------------------------------------
                # Update logical trade state
                # ----------------------------------------

                check_position_result(data)

                # ----------------------------------------
                # Break-even
                # ----------------------------------------

                if ENABLE_BREAK_EVEN:

                    manage_break_even(
                        data
                    )

                # ----------------------------------------
                # Trailing stop
                # ----------------------------------------

                if ENABLE_TRAILING_STOP:

                    manage_trailing_stop(
                        data
                    )

            except Exception as exc:

                logger.exception(
                    f"POSITION PROCESS ERROR "
                    f"{exc}"
                )

        return active

    except Exception as exc:

        logger.exception(
            f"POSITION MONITOR ERROR {exc}"
        )

        return []


# ============================================================
# Position Result
# ============================================================

def check_position_result(
    position: Dict[str, Any]
):
    """
    Update database state based on current floating P/L.

    This does NOT mean the trade is closed.
    It only reports the current state.
    """

    try:

        ticket = position.get(
            "ticket"
        )

        profit = float(
            position.get(
                "profit",
                0
            )
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
# Calculate Profit Percent
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

        if position_type == mt5.POSITION_TYPE_BUY:

            profit_percent = (
                (current - entry)
                / entry
            ) * 100

        else:

            profit_percent = (
                (entry - current)
                / entry
            ) * 100

        return float(
            profit_percent
        )

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
    """
    Move SL to entry once the position reaches
    the configured profit threshold.
    """

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
            )
        )

        if not ticket or not symbol:

            return False

        if entry <= 0:

            return False

        profit_percent = calculate_profit_percent(
            position
        )

        if profit_percent < BREAK_EVEN_TRIGGER_PERCENT:

            return False

        # ------------------------------------------------
        # BUY
        # ------------------------------------------------

        if position.get("type") == mt5.POSITION_TYPE_BUY:

            # Already protected
            if current_sl >= entry and current_sl != 0:

                return False

            new_sl = (
                entry *
                (
                    1
                    +
                    BREAK_EVEN_OFFSET_PERCENT / 100
                )
            )

        # ------------------------------------------------
        # SELL
        # ------------------------------------------------

        else:

            if current_sl <= entry and current_sl != 0:

                return False

            new_sl = (
                entry *
                (
                    1
                    -
                    BREAK_EVEN_OFFSET_PERCENT / 100
                )
            )

        new_sl = normalize_price(
            symbol,
            new_sl
        )

        if new_sl is None:

            return False

        logger.info(
            f"BREAK EVEN "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"NEW_SL={new_sl}"
        )

        return modify_position_sl(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=position.get("tp")
        )

    except Exception as exc:

        logger.error(
            f"BREAK EVEN ERROR {exc}"
        )

        return False


# ============================================================
# Trailing Stop
# ============================================================

def manage_trailing_stop(
    position: Dict[str, Any]
) -> bool:
    """
    Dynamically move SL in the direction of profit.
    """

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
            )
        )

        tp = position.get(
            "tp"
        )

        if not ticket or not symbol:

            return False

        if current <= 0:

            return False

        profit_percent = calculate_profit_percent(
            position
        )

        if profit_percent < TRAILING_START_PERCENT:

            return False

        # ------------------------------------------------
        # BUY
        # ------------------------------------------------

        if position.get("type") == mt5.POSITION_TYPE_BUY:

            new_sl = (
                current *
                (
                    1
                    -
                    TRAILING_DISTANCE_PERCENT / 100
                )
            )

            new_sl = normalize_price(
                symbol,
                new_sl
            )

            if new_sl is None:

                return False

            # Never move SL backwards.
            if current_sl > 0 and new_sl <= current_sl:

                return False

        # ------------------------------------------------
        # SELL
        # ------------------------------------------------

        else:

            new_sl = (
                current *
                (
                    1
                    +
                    TRAILING_DISTANCE_PERCENT / 100
                )
            )

            new_sl = normalize_price(
                symbol,
                new_sl
            )

            if new_sl is None:

                return False

            # Never move SL backwards.
            if current_sl > 0 and new_sl >= current_sl:

                return False

        logger.info(
            f"TRAILING STOP "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"OLD_SL={current_sl} "
            f"NEW_SL={new_sl}"
        )

        return modify_position_sl(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=tp
        )

    except Exception as exc:

        logger.error(
            f"TRAILING STOP ERROR {exc}"
        )

        return False


# ============================================================
# Modify SL / TP
# ============================================================

def modify_position_sl(
    ticket: int,
    symbol: str,
    sl: Optional[float] = None,
    tp: Optional[float] = None
) -> bool:
    """
    Modify an existing MT5 position's SL / TP.
    """

    try:

        if not is_connected():

            logger.error(
                "MODIFY POSITION: MT5 NOT CONNECTED"
            )

            return False

        if ticket is None:

            return False

        info = get_symbol_info(
            symbol
        )

        if info is None:

            return False

        if sl is not None:

            sl = normalize_price(
                symbol,
                sl
            )

        if tp is not None:

            tp = normalize_price(
                symbol,
                tp
            )

        request = {

            "action":
                mt5.TRADE_ACTION_SLTP,

            "symbol":
                symbol,

            "position":
                int(ticket),

            "magic":
                MAGIC_NUMBER

        }

        if sl is not None:

            request["sl"] = float(sl)

        if tp is not None:

            request["tp"] = float(tp)

        result = mt5.order_send(
            request
        )

        if result is None:

            logger.error(
                f"MODIFY POSITION FAILED "
                f"TICKET={ticket} "
                f"ERROR={mt5.last_error()}"
            )

            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:

            logger.error(
                f"MODIFY POSITION ERROR "
                f"TICKET={ticket} "
                f"RETCODE={result.retcode} "
                f"COMMENT={result.comment}"
            )

            return False

        logger.info(
            f"POSITION MODIFIED "
            f"TICKET={ticket} "
            f"SL={sl} "
            f"TP={tp}"
        )

        return True

    except Exception as exc:

        logger.exception(
            f"MODIFY POSITION ERROR {exc}"
        )

        return False


# ============================================================
# Close Position
# ============================================================

def close_position(
    ticket: int
) -> bool:
    """
    Close an existing MT5 position by ticket.
    """

    try:

        if not is_connected():

            logger.error(
                "CLOSE POSITION: MT5 NOT CONNECTED"
            )

            return False

        positions = mt5.positions_get(
            ticket=int(ticket)
        )

        if not positions:

            logger.warning(
                f"POSITION NOT FOUND "
                f"TICKET={ticket}"
            )

            return False

        position = positions[0]

        symbol = position.symbol

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            return False

        # ------------------------------------------------
        # Reverse the position
        # ------------------------------------------------

        if position.type == mt5.POSITION_TYPE_BUY:

            order_type = mt5.ORDER_TYPE_SELL

            price = float(
                tick.bid
            )

        else:

            order_type = mt5.ORDER_TYPE_BUY

            price = float(
                tick.ask
            )

        price = normalize_price(
            symbol,
            price
        )

        filling_mode = get_filling_mode(
            symbol
        )

        request = {

            "action":
                mt5.TRADE_ACTION_DEAL,

            "position":
                int(ticket),

            "symbol":
                symbol,

            "volume":
                float(position.volume),

            "type":
                order_type,

            "price":
                price,

            "deviation":
                DEVIATION,

            "magic":
                MAGIC_NUMBER,

            "comment":
                "Close Pourya Trader AI",

            "type_time":
                mt5.ORDER_TIME_GTC,

            "type_filling":
                filling_mode

        }

        logger.info(
            f"CLOSING POSITION "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"VOLUME={position.volume}"
        )

        result = mt5.order_send(
            request
        )

        if result is None:

            logger.error(
                f"CLOSE ORDER FAILED "
                f"TICKET={ticket} "
                f"ERROR={mt5.last_error()}"
            )

            return False

        if result.retcode not in (

            mt5.TRADE_RETCODE_DONE,

            mt5.TRADE_RETCODE_DONE_PARTIAL,

            mt5.TRADE_RETCODE_PLACED

        ):

            logger.error(
                f"CLOSE ORDER ERROR "
                f"TICKET={ticket} "
                f"RETCODE={result.retcode} "
                f"COMMENT={result.comment}"
            )

            return False

        logger.info(
            f"POSITION CLOSED "
            f"TICKET={ticket} "
            f"DEAL={result.deal}"
        )

        # ------------------------------------------------
        # Database
        # ------------------------------------------------

        try:

            final_profit = float(
                position.profit
            )

            if final_profit > 0:

                status = "WIN"

            elif final_profit < 0:

                status = "LOSS"

            else:

                status = "CLOSED"

            update_trade_status(
                ticket,
                status
            )

        except Exception as exc:

            logger.error(
                f"DATABASE CLOSE UPDATE ERROR "
                f"{exc}"
            )

        return True

    except Exception as exc:

        logger.exception(
            f"CLOSE POSITION ERROR {exc}"
        )

        return False


# ============================================================
# Close All Positions
# ============================================================

def close_all_positions() -> int:
    """
    Emergency close of all currently open positions.

    Returns number of successfully closed positions.
    """

    try:

        positions = get_open_positions()

        if not positions:

            return 0

        closed = 0

        for position in positions:

            ticket = position.get(
                "ticket"
            )

            if ticket is None:

                continue

            if close_position(
                ticket
            ):

                closed += 1

        logger.warning(
            f"CLOSE ALL POSITIONS "
            f"RESULT={closed}/{len(positions)}"
        )

        return closed

    except Exception as exc:

        logger.exception(
            f"CLOSE ALL ERROR {exc}"
        )

        return 0


# ============================================================
# Get Active Positions
# ============================================================

def get_active_positions(
    symbol: Optional[str] = None
):

    try:

        return get_open_positions(
            symbol=symbol
        )

    except Exception as exc:

        logger.error(
            f"GET ACTIVE POSITIONS ERROR {exc}"
        )

        return []
