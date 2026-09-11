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
    close_position as mt5_close_position,
)

from config import (
    DEFAULT_LOT,
    PAPER_TRADING,
    ALLOW_LIVE_TRADING,
    MAX_OPEN_TRADES,
)


# ============================================================
# Configuration
# ============================================================

MAGIC_NUMBER = 20260731

# Maximum total open positions allowed by the trading system.
#
# This is intentionally taken from config so the position
# limit has one central configuration source.
MAX_OPEN_POSITIONS = int(MAX_OPEN_TRADES)

# Absolute project-level volume ceiling for the pilot.
#
# Even if broker configuration permits a larger volume,
# Pourya Trader AI must never exceed this limit.
MAX_PROJECT_LOT = 0.03

DEFAULT_DEVIATION = 20

# Pilot symbol.
#
# The current controlled test account uses XAUUSD.su.
PILOT_SYMBOL = "XAUUSD.su"


# ============================================================
# Helpers
# ============================================================

def _normalize_symbol(
    symbol: str,
) -> str:

    return str(
        symbol or ""
    ).strip().upper()


def _normalize_side(
    side: str,
) -> Optional[str]:

    if side is None:
        return None

    side = str(
        side
    ).upper().strip()

    if side in (
        "BUY",
        "STRONG BUY",
    ):
        return "BUY"

    if side in (
        "SELL",
        "STRONG SELL",
    ):
        return "SELL"

    return None


def _live_trading_allowed() -> bool:
    """
    Independent safety gate for real MT5 orders.

    PAPER_TRADING must be False AND
    ALLOW_LIVE_TRADING must be True.

    Any configuration uncertainty fails closed.
    """

    try:

        if PAPER_TRADING:

            return False

        if not ALLOW_LIVE_TRADING:

            logger.critical(
                "LIVE TRADING BLOCKED: "
                "ALLOW_LIVE_TRADING=False"
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            f"LIVE TRADING SAFETY CHECK ERROR {exc}"
        )

        # Fail-safe:
        # never allow a real order when the safety
        # configuration cannot be verified.
        return False


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

        if positions is None:

            logger.error(
                "POSITION LIST RETURNED NONE"
            )

            # Fail-safe for position-limit decisions.
            return MAX_OPEN_POSITIONS

        return len(positions)

    except Exception as exc:

        logger.error(
            f"POSITION COUNT ERROR {exc}"
        )

        # Fail-safe for position-limit decisions.
        return MAX_OPEN_POSITIONS


# ============================================================
# Existing Symbol Position
# ============================================================

def has_open_position(
    symbol: str,
) -> bool:

    try:

        normalized_symbol = _normalize_symbol(
            symbol
        )

        if not normalized_symbol:

            return False

        positions = get_open_positions(
            symbol=normalized_symbol,
        )

        if positions is None:

            logger.error(
                f"OPEN POSITION LIST RETURNED NONE "
                f"{normalized_symbol}"
            )

            # Fail closed.
            return True

        return len(positions) > 0

    except Exception as exc:

        logger.error(
            f"OPEN POSITION CHECK ERROR "
            f"{symbol} {exc}"
        )

        # Fail-safe:
        # if we cannot verify existing positions,
        # do NOT allow a new trade.
        return True


# ============================================================
# Symbol Validation
# ============================================================

def validate_symbol(
    symbol: str,
) -> bool:

    try:

        normalized_symbol = _normalize_symbol(
            symbol
        )

        if not normalized_symbol:

            return False

        # ----------------------------------------------------
        # Pilot symbol restriction
        # ----------------------------------------------------
        #
        # During the controlled 7-day test, only XAUUSD.su
        # is permitted.
        #
        # This prevents an unexpected symbol from reaching
        # the execution layer.
        # ----------------------------------------------------

        if normalized_symbol != PILOT_SYMBOL.upper():

            logger.error(
                f"PILOT SYMBOL REJECTED "
                f"REQUESTED={normalized_symbol} "
                f"ALLOWED={PILOT_SYMBOL}"
            )

            return False

        info = get_symbol_info(
            normalized_symbol,
        )

        if info is None:

            logger.error(
                f"SYMBOL NOT FOUND "
                f"{normalized_symbol}"
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
    tp: Optional[float],
) -> bool:

    try:

        normalized_symbol = _normalize_symbol(
            symbol
        )

        tick = get_symbol_tick(
            normalized_symbol,
        )

        if tick is None:

            return False

        side = _normalize_side(
            side,
        )

        if side is None:

            return False

        if sl is None or tp is None:

            logger.error(
                f"MISSING SL/TP "
                f"{normalized_symbol}"
            )

            return False

        sl = float(sl)
        tp = float(tp)

        if sl <= 0 or tp <= 0:

            logger.error(
                f"INVALID SL/TP VALUES "
                f"{normalized_symbol} "
                f"SL={sl} "
                f"TP={tp}"
            )

            return False

        if side == "BUY":

            current_price = float(
                tick.ask
            )

            if current_price <= 0:

                return False

            if sl >= current_price:

                logger.error(
                    f"INVALID BUY SL "
                    f"{normalized_symbol} "
                    f"SL={sl} "
                    f"PRICE={current_price}"
                )

                return False

            if tp <= current_price:

                logger.error(
                    f"INVALID BUY TP "
                    f"{normalized_symbol} "
                    f"TP={tp} "
                    f"PRICE={current_price}"
                )

                return False

        else:

            current_price = float(
                tick.bid
            )

            if current_price <= 0:

                return False

            if sl <= current_price:

                logger.error(
                    f"INVALID SELL SL "
                    f"{normalized_symbol} "
                    f"SL={sl} "
                    f"PRICE={current_price}"
                )

                return False

            if tp >= current_price:

                logger.error(
                    f"INVALID SELL TP "
                    f"{normalized_symbol} "
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
    lot: float,
):

    try:

        lot = float(lot)

        if lot <= 0:

            logger.error(
                f"INVALID NON-POSITIVE VOLUME "
                f"{symbol} LOT={lot}"
            )

            return None

        # ----------------------------------------------------
        # Project hard ceiling
        # ----------------------------------------------------

        if lot > MAX_PROJECT_LOT:

            logger.warning(
                f"PROJECT LOT LIMIT APPLIED "
                f"{symbol} "
                f"REQUESTED={lot} "
                f"MAX={MAX_PROJECT_LOT}"
            )

            lot = MAX_PROJECT_LOT

        normalized = normalize_volume(
            symbol,
            lot,
        )

        if normalized is None:

            logger.error(
                f"INVALID VOLUME "
                f"{symbol}"
            )

            return None

        if normalized <= 0:

            return None

        # ----------------------------------------------------
        # Defense-in-depth after broker normalization
        # ----------------------------------------------------

        if normalized > MAX_PROJECT_LOT:

            logger.error(
                f"NORMALIZED VOLUME EXCEEDS "
                f"PROJECT LIMIT "
                f"{symbol} "
                f"VOLUME={normalized} "
                f"MAX={MAX_PROJECT_LOT}"
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
# Position Limit
# ============================================================

def validate_position_limit() -> bool:

    try:

        count = get_position_count()

        if count < 0:

            logger.error(
                f"INVALID POSITION COUNT "
                f"{count}"
            )

            return False

        if count >= MAX_OPEN_POSITIONS:

            logger.warning(
                f"MAX OPEN POSITIONS "
                f"{count}/{MAX_OPEN_POSITIONS}"
            )

            return False

        logger.info(
            f"POSITION CAP OK "
            f"{count}/{MAX_OPEN_POSITIONS}"
        )

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
    tp: float,
) -> bool:

    if not check_connection():

        return False

    normalized_symbol = _normalize_symbol(
        symbol
    )

    side = _normalize_side(
        side,
    )

    if side is None:

        logger.error(
            "INVALID ORDER SIDE"
        )

        return False

    if not validate_symbol(
        normalized_symbol,
    ):

        return False

    # --------------------------------------------------------
    # Global position limit
    # --------------------------------------------------------

    if not validate_position_limit():

        return False

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT reject an order simply because another position
    # already exists for the same symbol.
    #
    # The pilot allows up to MAX_OPEN_POSITIONS total
    # positions, including multiple XAUUSD.su positions.
    # --------------------------------------------------------

    volume = validate_volume(
        normalized_symbol,
        lot,
    )

    if volume is None:

        return False

    if not validate_prices(
        normalized_symbol,
        side,
        sl,
        tp,
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
    comment: str = "Pourya Trader AI",
) -> Optional[Dict[str, Any]]:

    try:

        original_side = side

        normalized_symbol = _normalize_symbol(
            symbol
        )

        side = _normalize_side(
            side,
        )

        if side is None:

            logger.error(
                f"INVALID SIDE "
                f"{original_side}"
            )

            return None

        if not validate_order(
            normalized_symbol,
            side,
            lot,
            sl,
            tp,
        ):

            logger.warning(
                f"ORDER REJECTED "
                f"{normalized_symbol} "
                f"{side}"
            )

            return None

        volume = validate_volume(
            normalized_symbol,
            lot,
        )

        sl = normalize_price(
            normalized_symbol,
            sl,
        )

        tp = normalize_price(
            normalized_symbol,
            tp,
        )

        if (
            volume is None
            or sl is None
            or tp is None
        ):

            return None

        tick = get_symbol_tick(
            normalized_symbol,
        )

        if tick is None:

            return None

        if side == "BUY":

            expected_price = float(
                tick.ask
            )

        else:

            expected_price = float(
                tick.bid
            )

        if expected_price <= 0:

            logger.error(
                f"INVALID MARKET PRICE "
                f"{normalized_symbol} "
                f"{side}"
            )

            return None

        expected_price = normalize_price(
            normalized_symbol,
            expected_price,
        )

        logger.info(
            "================================"
        )

        logger.info(
            f"MT5 MARKET ORDER "
            f"{normalized_symbol} {side}"
        )

        logger.info(
            f"LOT={volume} "
            f"PRICE={expected_price} "
            f"SL={sl} "
            f"TP={tp}"
        )

        if confidence is not None:

            logger.info(
                f"CONFIDENCE={confidence}"
            )

        logger.info(
            f"OPEN_POSITIONS="
            f"{get_position_count()}/"
            f"{MAX_OPEN_POSITIONS}"
        )

        logger.info(
            f"MAX_PROJECT_LOT="
            f"{MAX_PROJECT_LOT}"
        )

        logger.info(
            f"PAPER_TRADING="
            f"{PAPER_TRADING}"
        )

        logger.info(
            f"ALLOW_LIVE_TRADING="
            f"{ALLOW_LIVE_TRADING}"
        )

        logger.info(
            "================================"
        )

        # ====================================================
        # PAPER TRADING
        # ====================================================

        if PAPER_TRADING:

            logger.warning(
                "PAPER TRADING ACTIVE - "
                "NO REAL ORDER WILL BE SENT"
            )

            return {

                "success": True,

                "paper_trading": True,

                "symbol": normalized_symbol,

                "side": side,

                "volume": volume,

                "price": expected_price,

                "sl": sl,

                "tp": tp,

                "ticket": None,

                "order": None,

                "deal": None,

                "confidence": confidence,

                "status": "PAPER_OPEN",

            }

        # ====================================================
        # LIVE TRADING SAFETY GATE
        # ====================================================

        if not _live_trading_allowed():

            logger.critical(
                "REAL MT5 ORDER BLOCKED "
                f"{normalized_symbol} {side} "
                "BY SAFETY GATE"
            )

            return None

        # ====================================================
        # REAL MT5 ORDER
        # ====================================================

        result = send_market_order(

            symbol=normalized_symbol,

            side=side,

            volume=volume,

            sl=sl,

            tp=tp,

            magic=MAGIC_NUMBER,

            deviation=DEFAULT_DEVIATION,

            comment=comment,

        )

        if not result:

            logger.error(
                f"MT5 ORDER FAILED "
                f"{normalized_symbol}"
            )

            return None

        if not result.get(
            "success",
            False,
        ):

            logger.error(
                "MT5 ORDER REJECTED "
                f"{normalized_symbol} "
                f"RETCODE={result.get('retcode')} "
                f"ERROR={result.get('error')}"
            )

            return None

        # ----------------------------------------------------
        # Connector exposes:
        # order = MT5 order ticket
        # deal  = executed deal ticket
        # ----------------------------------------------------

        order = result.get(
            "order"
        )

        deal = result.get(
            "deal"
        )

        # Backward-compatible ticket.
        #
        # Prefer the MT5 order ticket when available.
        # If it is unavailable, use deal as fallback.
        ticket = order

        if ticket is None:

            ticket = deal

        if ticket is None:

            logger.error(
                f"ORDER WITHOUT MT5 TICKET "
                f"{normalized_symbol} "
                f"ORDER={order} "
                f"DEAL={deal}"
            )

            # IMPORTANT:
            # Do not retry here automatically.
            # An ambiguous broker response must never
            # trigger a blind duplicate order.
            return None

        response = {

            "success": True,

            "paper_trading": False,

            "symbol": normalized_symbol,

            "side": side,

            "volume": volume,

            "price": result.get(
                "price",
                expected_price,
            ),

            "sl": sl,

            "tp": tp,

            "ticket": ticket,

            "order": order,

            "deal": deal,

            "confidence": confidence,

            "status": "OPEN",

        }

        logger.info(
            f"MT5 POSITION OPENED "
            f"TICKET={ticket} "
            f"ORDER={order} "
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
    confidence: Optional[float] = None,
):

    """
    Backward-compatible wrapper.

    MT5 determines the actual market entry price.
    The supplied entry is therefore used for
    logging/compatibility only.
    """

    try:

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

            confidence=confidence,

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
    ticket: int,
) -> bool:

    try:

        if ticket is None:

            return False

        # ----------------------------------------------------
        # Paper positions are managed by the paper position
        # manager.
        #
        # This compatibility function must not attempt
        # a real MT5 close while PAPER_TRADING is active.
        # ----------------------------------------------------

        if PAPER_TRADING:

            logger.info(
                f"PAPER POSITION CLOSE REQUEST "
                f"TICKET={ticket}"
            )

            return True

        # ----------------------------------------------------
        # Independent live safety gate.
        # ----------------------------------------------------

        if not _live_trading_allowed():

            logger.critical(
                "REAL MT5 CLOSE BLOCKED "
                f"TICKET={ticket} "
                "BY SAFETY GATE"
            )

            return False

        result = mt5_close_position(
            ticket,
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
    symbol: Optional[str] = None,
):

    try:

        if symbol is not None:

            symbol = _normalize_symbol(
                symbol
            )

        return get_open_positions(
            symbol=symbol,
        )

    except Exception as exc:

        logger.error(
            f"GET POSITIONS ERROR "
            f"{exc}"
        )

        return []


# ============================================================
# Find Position
# ============================================================

def get_position(
    symbol: str,
):

    try:

        normalized_symbol = _normalize_symbol(
            symbol
        )

        positions = get_open_positions(
            symbol=normalized_symbol,
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

