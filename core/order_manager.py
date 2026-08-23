# core/order_manager.py

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

from core.position_manager import (
    close_position as mt5_close_position
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

def _normalize_side(
    side: str
) -> Optional[str]:

    if side is None:
        return None

    side = str(
        side
    ).upper().strip()

    if side in (
        "BUY",
        "STRONG BUY"
    ):
        return "BUY"

    if side in (
        "SELL",
        "STRONG SELL"
    ):
        return "SELL"

    return None


# ============================================================
# Connection
# ============================================================

def check_connection() -> bool:

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
                "ACCOUNT INFO UNAVAILABLE"
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

        return len(
            positions
        )

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

        return len(
            positions
        ) > 0

    except Exception as exc:

        logger.error(
            f"OPEN POSITION CHECK ERROR "
            f"{symbol} {exc}"
        )

        return True


# ============================================================
# Symbol Validation
# ============================================================

def validate_symbol(
    symbol: str
) -> bool:

    try:

        if not symbol:

            return False

        info = get_symbol_info(
            symbol
        )

        if info is None:

            logger.error(
                f"SYMBOL NOT FOUND {symbol}"
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

        if sl <= 0 or tp <= 0:

            return False

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

        else:

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

        lot = float(
            lot
        )

        if lot <= 0:

            return None

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

            return None

        return normalized

    except Exception as exc:

        logger.error(
            f"VOLUME VALIDATION ERROR "
            f"{symbol} {exc}"
        )

        return None


# ============================================================
# Position Limit
# ============================================================

def validate_position_limit() -> bool:

    try:

        count = get_position_count()

        if count >= MAX_OPEN_POSITIONS:

            logger.warning(
                f"MAX OPEN POSITIONS "
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
# Order Validation
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
            "INVALID ORDER SIDE"
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

    if validate_volume(
        symbol,
        lot
    ) is None:

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
# Open Market Position
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

            return None

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

        if (
            volume is None
            or sl is None
            or tp is None
        ):

            return None

        logger.info(
            "================================"
        )

        logger.info(
            f"MT5 MARKET ORDER "
            f"{symbol} {side}"
        )

        logger.info(
            f"LOT={volume} "
            f"SL={sl} "
            f"TP={tp}"
        )

        if confidence is not None:

            logger.info(
                f"CONFIDENCE={confidence}"
            )

        logger.info(
            "================================"
        )

        result = send_market_order(

            symbol=symbol,

            side=side,

            lot=volume,

            sl=sl,

            tp=tp

        )

        if not result:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{symbol}"
            )

            return None

        ticket = result.get(
            "ticket"
        )

        deal = result.get(
            "deal"
        )

        if ticket is None:

            logger.error(
                f"ORDER WITHOUT TICKET "
                f"{symbol}"
            )

            return None

        response = {

            "success": True,

            "symbol":
                symbol,

            "side":
                side,

            "volume":
                volume,

            "price":
                result.get(
                    "price"
                ),

            "sl":
                sl,

            "tp":
                tp,

            "ticket":
                ticket,

            "deal":
                deal,

            "confidence":
                confidence,

            "status":
                "OPEN"

        }

        logger.info(
            f"MT5 POSITION OPENED "
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
# Create Order Compatibility Wrapper
# ============================================================

def create_order(
    symbol: str,
    side: str,
    entry: float,
    tp: float,
    sl: float,
    lot: Optional[float] = None,
    confidence: Optional[float] = None
):

    """
    Backward-compatible wrapper.

    The MT5 market price is determined by the broker.
    Therefore entry is used for validation/logging only.
    """

    try:

        from config import DEFAULT_LOT

        if lot is None:

            lot = DEFAULT_LOT

        logger.info(
            f"CREATE ORDER "
            f"{symbol} {side} "
            f"EXPECTED_ENTRY={entry}"
        )

        return open_market_position(

            symbol=symbol,

            side=side,

            lot=lot,

            sl=sl,

            tp=tp,

            confidence=confidence

        )

    except Exception as exc:

        logger.exception(
            f"CREATE ORDER ERROR {exc}"
        )

        return None


# ============================================================
# Close Position
# ============================================================

def close_position(
    ticket: int
) -> bool:

    try:

        if ticket is None:

            return False

        result = mt5_close_position(
            ticket
        )

        if result:

            logger.info(
                f"POSITION CLOSED "
                f"TICKET={ticket}"
            )

            return True

        logger.error(
            f"POSITION CLOSE FAILED "
            f"TICKET={ticket}"
        )

        return False

    except Exception as exc:

        logger.exception(
            f"CLOSE POSITION ERROR "
            f"TICKET={ticket} {exc}"
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
