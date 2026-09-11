from __future__ import annotations

from typing import Any, Optional

from config import (
    ALLOW_LIVE_TRADING,
    DEFAULT_LOT,
    MAX_OPEN_TRADES,
    PAPER_TRADING,
)

from core.logger import logger

from core.mt5_connector import (
    DEFAULT_COMMENT,
    DEFAULT_MAGIC,
    MAX_PROJECT_LOT,
    MIN_PROJECT_LOT,
    PILOT_SYMBOL,
    ensure_connection,
    get_account_info,
    get_open_position_count,
    get_symbol_info,
    get_symbol_tick,
    normalize_price,
    normalize_volume,
    send_market_order,
)

from core.position_manager import (
    close_position as manager_close_position,
)


MAGIC_NUMBER = DEFAULT_MAGIC

MAX_OPEN_POSITIONS = min(
    int(MAX_OPEN_TRADES),
    5,
)

PROJECT_SYMBOL = PILOT_SYMBOL


def _live_gate_open() -> bool:

    if bool(PAPER_TRADING):
        return False

    if not bool(ALLOW_LIVE_TRADING):
        return False

    return True


def check_connection() -> bool:

    try:
        return bool(
            ensure_connection()
        )
    except Exception:
        return False


def get_account():

    try:
        return get_account_info()
    except Exception:
        return None


def get_position_count(
    symbol: str = PROJECT_SYMBOL,
) -> int:

    if symbol != PROJECT_SYMBOL:
        return MAX_OPEN_POSITIONS

    try:

        return int(
            get_open_position_count(
                symbol,
                MAGIC_NUMBER,
            )
        )

    except Exception as exc:

        logger.exception(
            "ORDER MANAGER: POSITION COUNT ERROR: %s",
            exc,
        )

        # Fail closed.
        return MAX_OPEN_POSITIONS


def has_open_position(
    symbol: str = PROJECT_SYMBOL,
) -> bool:

    try:
        return (
            get_position_count(symbol) > 0
        )
    except Exception:
        return True


def _validate_symbol(
    symbol: str,
) -> bool:

    return (
        isinstance(symbol, str)
        and symbol.strip() == PROJECT_SYMBOL
    )


def _validate_side(
    side: str,
) -> bool:

    return str(side).upper().strip() in {
        "BUY",
        "SELL",
    }


def _validate_price(
    symbol: str,
    price: float,
) -> bool:

    if not _validate_symbol(symbol):
        return False

    try:
        requested = float(price)
    except Exception:
        return False

    if requested <= 0:
        return False

    tick = get_symbol_tick(symbol)

    if tick is None:
        return False

    return True


def _validate_volume(
    symbol: str,
    volume: float,
) -> float:

    try:
        requested = float(volume)
    except Exception:
        return 0.0

    if requested < MIN_PROJECT_LOT:
        return 0.0

    # HARD REJECT.
    if requested > MAX_PROJECT_LOT:
        logger.warning(
            "ORDER MANAGER: LOT %.4f EXCEEDS HARD LIMIT %.4f",
            requested,
            MAX_PROJECT_LOT,
        )
        return 0.0

    normalized = normalize_volume(
        symbol,
        requested,
    )

    if normalized < MIN_PROJECT_LOT:
        return 0.0

    if normalized > MAX_PROJECT_LOT:
        return 0.0

    return normalized


def _validate_position_limit(
    symbol: str,
) -> bool:

    count = get_position_count(symbol)

    if count >= MAX_OPEN_POSITIONS:

        logger.warning(
            "ORDER MANAGER: POSITION LIMIT REACHED "
            "%s/%s",
            count,
            MAX_OPEN_POSITIONS,
        )

        return False

    return True


def validate_order(
    symbol: str,
    side: str,
    lot: float,
    price: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
) -> bool:

    if not check_connection():
        return False

    if not _validate_symbol(symbol):
        return False

    if not _validate_side(side):
        return False

    if not _validate_position_limit(symbol):
        return False

    normalized_lot = _validate_volume(
        symbol,
        lot,
    )

    if normalized_lot <= 0:
        return False

    if not _validate_price(
        symbol,
        price,
    ):
        return False

    if sl is not None:

        try:
            if float(sl) <= 0:
                return False
        except Exception:
            return False

    if tp is not None:

        try:
            if float(tp) <= 0:
                return False
        except Exception:
            return False

    return True


def open_market_position(
    symbol: str,
    side: str,
    lot: float = DEFAULT_LOT,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    confidence: Optional[float] = None,
    comment: str = DEFAULT_COMMENT,
    **kwargs: Any,
):

    side = str(side).upper().strip()

    if not _validate_symbol(symbol):
        return None

    tick = get_symbol_tick(symbol)

    if tick is None:
        return None

    price = (
        float(tick.ask)
        if side == "BUY"
        else float(tick.bid)
    )

    normalized_lot = _validate_volume(
        symbol,
        lot,
    )

    if normalized_lot <= 0:
        return None

    if not validate_order(
        symbol,
        side,
        normalized_lot,
        price,
        sl,
        tp,
    ):
        return None

    # --------------------------------------------------------
    # PAPER MODE
    # --------------------------------------------------------

    if bool(PAPER_TRADING):

        logger.info(
            "ORDER MANAGER: PAPER ORDER "
            "%s %s LOT=%s PRICE=%s",
            side,
            symbol,
            normalized_lot,
            price,
        )

        return {
            "success": True,
            "paper": True,
            "live": False,
            "symbol": symbol,
            "side": side,
            "volume": normalized_lot,
            "price": price,
            "sl": sl,
            "tp": tp,
            "ticket": None,
            "order": None,
            "deal": None,
            "confidence": confidence,
        }

    # --------------------------------------------------------
    # LIVE HARD GATE
    # --------------------------------------------------------

    if not _live_gate_open():

        logger.warning(
            "ORDER MANAGER: LIVE ORDER BLOCKED"
        )

        return None

    # --------------------------------------------------------
    # FINAL CONNECTOR GATE
    # --------------------------------------------------------

    result = send_market_order(
        symbol=symbol,
        side=side,
        volume=normalized_lot,
        sl=float(sl),
        tp=float(tp),
        magic=MAGIC_NUMBER,
        comment=comment,
    )

    if result is None:

        logger.error(
            "ORDER MANAGER: MT5 ORDER FAILED"
        )

        return None

    order_id = getattr(
        result,
        "order",
        0,
    )

    deal_id = getattr(
        result,
        "deal",
        0,
    )

    return {
        "success": True,
        "paper": False,
        "live": True,
        "symbol": symbol,
        "side": side,
        "volume": normalized_lot,
        "price": price,
        "sl": sl,
        "tp": tp,
        "ticket": order_id or deal_id,
        "order": order_id,
        "deal": deal_id,
        "confidence": confidence,
        "retcode": getattr(
            result,
            "retcode",
            None,
        ),
    }


def create_order(
    *args,
    **kwargs,
):

    return open_market_position(
        *args,
        **kwargs,
    )


def close_position(
    ticket: int,
):

    if not _live_gate_open():

        if bool(PAPER_TRADING):
            return manager_close_position(ticket)

        return False

    return manager_close_position(ticket)


def get_positions():

    try:

        from core.mt5_connector import (
            get_project_positions,
        )

        return get_project_positions(
            PROJECT_SYMBOL,
            MAGIC_NUMBER,
        )

    except Exception:

        return []


def get_position(
    ticket: int,
):

    try:

        positions = get_positions()

        for position in positions:

            if int(
                getattr(
                    position,
                    "ticket",
                    -1,
                )
            ) == int(ticket):

                return position

    except Exception:
        pass

    return None


__all__ = [
    "open_market_position",
    "create_order",
    "close_position",
    "validate_order",
    "get_position_count",
    "has_open_position",
    "get_positions",
    "get_position",
]
