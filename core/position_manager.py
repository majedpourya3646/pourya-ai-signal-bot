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
# Position Management
# ------------------------------------------------------------

ENABLE_BREAK_EVEN = True

ENABLE_TRAILING_STOP = True

# درصد سود برای فعال شدن Break Even
BREAK_EVEN_TRIGGER_PERCENT = 1.0

# مقدار محافظت اطراف Entry
BREAK_EVEN_OFFSET_PERCENT = 0.05

# درصد سود برای شروع Trailing
TRAILING_START_PERCENT = 1.5

# فاصله Trailing از قیمت
TRAILING_DISTANCE_PERCENT = 0.75


# ============================================================
# MT5 Position Type Helpers
# ============================================================

def is_buy_position(
    position
) -> bool:

    return (
        position.get("type")
        == mt5.POSITION_TYPE_BUY
    )


def is_sell_position(
    position
) -> bool:

    return (
        position.get("type")
        == mt5.POSITION_TYPE_SELL
    )


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

                # ------------------------------------------------
                # Only manage Pourya Trader AI positions
                # ------------------------------------------------

                magic = position.get(
                    "magic"
                )

                if (
                    magic is not None
                    and int(magic) != MAGIC_NUMBER
                ):

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
                # Database state
                # ------------------------------------------------

                check_position_result(
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
# Position Result
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

        elif position_type == mt5.POSITION_TYPE_SELL:

            profit_percent = (
                (entry - current)
                / entry
            ) * 100

        else:

            return 0.0

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

        if is_buy_position(position):

            # Already protected
            if (
                current_sl > 0
                and current_sl >= entry
            ):

                return False

            new_sl = (
                entry
                * (
                    1
                    + BREAK_EVEN_OFFSET_PERCENT / 100
                )
            )

        # ------------------------------------------------
        # SELL
        # ------------------------------------------------

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
                    - BREAK_EVEN_OFFSET_PERCENT / 100
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

        logger.info(
            f"BREAK EVEN "
            f"TICKET={ticket} "
            f"SYMBOL={symbol} "
            f"PROFIT={profit_percent:.2f}% "
            f"NEW_SL={new_sl}"
        )

        return modify_position_sl(
            ticket=ticket,
            symbol=symbol,
            sl=new_sl,
            tp=position.get("tp")
        )

    except Exception as exc:

       
