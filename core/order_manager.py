from typing import Optional, Dict, Any

from core.logger import logger

from core.mt5_connector import (
    is_connected,
    get_account_info,
    get_symbol_info,
    get_symbol_tick,
    normalize_volume,
    normalize_price,
    get_open_positions,
    send_market_order,
)


# ============================================================
# Configuration
# ============================================================

MAGIC_NUMBER = 20260731

MAX_OPEN_POSITIONS = 3

DEFAULT_DEVIATION = 20


# ============================================================
# Helpers
# ============================================================

def _normalize_side(side: str) -> Optional[str]:
    """
    Normalize BUY / SELL signal.
    """

    if side is None:
        return None

    side = str(side).upper().strip()

    if side in ("BUY", "STRONG BUY"):
        return "BUY"

    if side in ("SELL", "STRONG SELL"):
        return "SELL"

    return None


# ============================================================
# Connection
# ============================================================

def check_connection() -> bool:
    """
    Check MT5 connection before every execution.
    """

    try:

        if not is_connected():

            logger.error(
                "ORDER MANAGER: MT5 NOT CONNECTED"
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            f"ORDER MANAGER CONNECTION ERROR {exc}"
        )

        return False


# ============================================================
# Account
# ============================================================

def get_account():

    try:

        account = get_account_info()

        if account is None:

            logger.error(
                "ORDER MANAGER: ACCOUNT INFO UNAVAILABLE"
            )

            return None

        return account

    except Exception as exc:

        logger.exception(
            f"ACCOUNT READ ERROR {exc}"
        )

        return None


# ============================================================
# Position Count
# ============================================================

def get_position_count() -> int:

    try:

        positions = get_open_positions()

        return len(positions)

    except Exception as exc:

        logger.error(
            f"POSITION COUNT ERROR {exc}"
        )

        return 0


# ============================================================
# Existing Symbol Position
# ============================================================

def has_open_position(
    symbol: str
) -> bool:

    try:

        positions = get_open_positions(
            symbol=symbol
        )

        return len(positions) > 0

    except Exception as exc:

        logger.error(
            f"OPEN POSITION CHECK ERROR "
            f"{symbol} {exc}"
        )

        return False


# ============================================================
# Symbol Validation
# ============================================================

def validate_symbol(
    symbol: str
) -> bool:

    try:

        info = get_symbol_info(
            symbol
        )

        if info is None:

            logger.error(
                f"SYMBOL VALIDATION FAILED {symbol}"
            )

            return False

        return True

    except Exception as exc:

        logger.error(
            f"SYMBOL VALIDATION ERROR "
            f"{symbol} {exc}"
        )

        return False


# ============================================================
# Price Validation
# ============================================================

def validate_prices(
    symbol: str,
    side: str,
    sl: Optional[float],
    tp: Optional[float]
) -> bool:

    try:

        tick = get_symbol_tick(
            symbol
        )

        if tick is None:

            return False

        side = _normalize_side(
            side
        )

        if side is None:

            return False

        if sl is None or tp is None:

            logger.error(
                f"MISSING SL/TP {symbol}"
            )

            return False

        sl = float(sl)
        tp = float(tp)

        if side == "BUY":

            current_price = float(
                tick.ask
            )

            if sl >= current_price:

                logger.error(
                    f"INVALID BUY SL "
                    f"{symbol} "
                    f"SL={sl} "
                    f"PRICE={current_price}"
                )

                return False

            if tp <= current_price:

                logger.error(
                    f"INVALID BUY TP "
                    f"{symbol} "
                    f"TP={tp} "
                    f"PRICE={current_price}"
                )

                return False

        elif side == "SELL":

            current_price = float(
                tick.bid
            )

            if sl <= current_price:

                logger.error(
                    f"INVALID SELL SL "
                    f"{symbol} "
                    f"SL={sl} "
                    f"PRICE={current_price}"
                )

                return False

            if tp >= current_price:

                logger.error(
                    f"INVALID SELL TP "
                    f"{symbol} "
                    f"TP={tp} "
                    f"PRICE={current_price}"
                )

                return False

        return True

    except Exception as exc:

        logger.exception(
            f"PRICE VALIDATION ERROR "
            f"{symbol} {exc}"
        )

        return False


# ============================================================
# Volume Validation
# ============================================================

def validate_volume(
    symbol: str,
    lot: float
):

    try:

        normalized = normalize_volume(
            symbol,
            lot
        )

        if normalized is None:

            logger.error(
                f"INVALID VOLUME {symbol}"
            )

            return None

        if normalized <= 0:

            logger.error(
                f"ZERO VOLUME {symbol}"
            )

            return None

        return normalized

    except Exception as exc:

        logger.error(
            f"VOLUME VALIDATION ERROR "
            f"{symbol} {exc}"
        )

        return None


# ============================================================
# Risk / Position Limit
# ============================================================

def validate_position_limit() -> bool:

    try:

        count = get_position_count()

        if count >= MAX_OPEN_POSITIONS:

            logger.warning(
                "MAX OPEN POSITIONS REACHED "
                f"{count}/{MAX_OPEN_POSITIONS}"
            )

            return False

        return True

    except Exception as exc:

        logger.error(
            f"POSITION LIMIT ERROR {exc}"
        )

        return False


# ============================================================
# Order Request Validation
# ============================================================

def validate_order(
    symbol: str,
    side: str,
    lot: float,
    sl: float,
    tp: float
) -> bool:

    if not check_connection():

        return False

    side = _normalize_side(
        side
    )

    if side is None:

        logger.error(
            f"INVALID SIDE {side}"
        )

        return False

    if not validate_symbol(
        symbol
    ):

        return False

    if not validate_position_limit():

        return False

    if has_open_position(
        symbol
    ):

        logger.warning(
            f"POSITION ALREADY EXISTS "
            f"{symbol}"
        )

        return False

    volume = validate_volume(
        symbol,
        lot
    )

    if volume is None:

        return False

    if not validate_prices(
        symbol,
        side,
        sl,
        tp
    ):

        return False

    return True


# ============================================================
# Execute Market Order
# ============================================================

def open_market_position(
    symbol: str,
    side: str,
    lot: float,
    sl: float,
    tp: float,
    confidence: Optional[float] = None,
    comment: str = "Pourya Trader AI"
) -> Optional[Dict[str, Any]]:

    try:

        side = _normalize_side(
            side
        )

        if side is None:

            logger.error(
                "ORDER REJECTED: INVALID SIDE"
            )

            return None

        # ----------------------------------------
        # Validate
        # ----------------------------------------

        if not validate_order(
            symbol,
            side,
            lot,
            sl,
            tp
        ):

            logger.warning(
                f"ORDER REJECTED "
                f"{symbol} {side}"
            )

            return None

        # ----------------------------------------
        # Normalize
        # ----------------------------------------

        volume = normalize_volume(
            symbol,
            lot
        )

        sl = normalize_price(
            symbol,
            sl
        )

        tp = normalize_price(
            symbol,
            tp
        )

        # ----------------------------------------
        # Log
        # ----------------------------------------

        logger.info(
            "================================"
        )

        logger.info(
            "MT5 MARKET ORDER"
        )

        logger.info(
            f"SYMBOL={symbol}"
        )

        logger.info(
            f"SIDE={side}"
        )

        logger.info(
            f"LOT={volume}"
        )

        logger.info(
            f"SL={sl}"
        )

        logger.info(
            f"TP={tp}"
        )

        if confidence is not None:

            logger.info(
                f"CONFIDENCE={confidence}"
            )

        logger.info(
            "================================"
        )

        # ----------------------------------------
        # Send
        # ----------------------------------------

        result = send_market_order(

            symbol=symbol,

            side=side,

            lot=volume,

            sl=sl,

            tp=tp

        )

        if result is None:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{symbol}"
            )

            return None

        # ----------------------------------------
        # Result
        # ----------------------------------------

        ticket = result.get(
            "ticket"
        )

        deal = result.get(
            "deal"
        )

        response = {

            "success": True,

            "symbol": symbol,

            "side": side,

            "volume": volume,

            "price": result.get(
                "price"
            ),

            "sl": sl,

            "tp": tp,

            "ticket": ticket,

            "deal": deal,

            "confidence": confidence,

            "status": "OPEN"

        }

        logger.info(
            f"MT5 POSITION OPENED "
            f"{symbol} "
            f"{side} "
            f"TICKET={ticket} "
            f"DEAL={deal}"
        )

        return response

    except Exception as exc:

        logger.exception(
            f"OPEN POSITION ERROR "
            f"{symbol} {exc}"
        )

        return None


# ============================================================
# Close Position
# ============================================================

def close_position(
    symbol: str
) -> bool:

    """
    Placeholder for the next Position Manager stage.

    Closing will be implemented through MT5
    using the opposite market order and
    position ticket.
    """

    logger.warning(
        f"CLOSE POSITION NOT IMPLEMENTED YET "
        f"{symbol}"
    )

    return False


# ============================================================
# Get Positions
# ============================================================

def get_positions(
    symbol: Optional[str] = None
):

    try:

        return get_open_positions(
            symbol=symbol
        )

    except Exception as exc:

        logger.error(
            f"GET POSITIONS ERROR {exc}"
        )

        return []


# ============================================================
# Find Position
# ============================================================

def get_position(
    symbol: str
):

    try:

        positions = get_open_positions(
            symbol=symbol
        )

        if not positions:

            return None

        return positions[0]

    except Exception as exc:

        logger.error(
            f"GET POSITION ERROR "
            f"{symbol} {exc}"
        )

        return None
