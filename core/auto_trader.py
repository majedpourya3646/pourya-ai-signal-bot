from __future__ import annotations

import math
from typing import Any, Optional

from config import (
    DEFAULT_LOT,
    MAX_OPEN_TRADES,
    MIN_CONFIDENCE,
    PAPER_TRADING,
)

from core.logger import logger

from core.order_manager import (
    get_position_count,
    open_market_position,
)

from core.trade_manager import (
    get_open_trades,
    save_trade,
)


PILOT_SYMBOL = "XAUUSD.su"

MIN_PROJECT_LOT = 0.01

MAX_PROJECT_LOT = 0.03

PROJECT_MAX_POSITIONS = min(
    5,
    int(MAX_OPEN_TRADES),
)


def _normalize_symbol(
    symbol: Any,
) -> str:

    return str(
        symbol or ""
    ).strip()


def _normalize_signal(
    signal: Any,
) -> str:

    return str(
        signal or ""
    ).strip().upper()


def _validate_opportunity(
    opportunity: dict[str, Any],
) -> bool:

    symbol = _normalize_symbol(
        opportunity.get("symbol")
        or opportunity.get("ticker")
        or opportunity.get("instrument")
    )

    side = _normalize_signal(
        opportunity.get("side")
        or opportunity.get("signal")
        or opportunity.get("direction")
    )

    if symbol != PILOT_SYMBOL:
        return False

    if side not in {"BUY", "SELL"}:
        return False

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
        )

    except Exception:

        return False

    if confidence < MIN_CONFIDENCE:
        return False

    try:

        entry = float(
            opportunity.get(
                "entry_price",
                opportunity.get(
                    "entry",
                    opportunity.get(
                        "price",
                        0,
                    ),
                ),
            )
        )

        sl = float(
            opportunity.get(
                "stop_loss",
                opportunity.get(
                    "sl",
                    0,
                ),
            )
        )

        tp = float(
            opportunity.get(
                "take_profit",
                opportunity.get(
                    "tp",
                    0,
                ),
            )
        )

    except Exception:

        return False

    if entry <= 0 or sl <= 0 or tp <= 0:
        return False

    if side == "BUY":

        if not (
            sl < entry < tp
        ):
            return False

    else:

        if not (
            tp < entry < sl
        ):
            return False

    return True


def _get_active_trade_count() -> int:

    if PAPER_TRADING:

        try:

            trades = get_open_trades()

            count = 0

            for trade in trades or []:

                symbol = _normalize_symbol(
                    trade.get("symbol")
                    if isinstance(
                        trade,
                        dict,
                    )
                    else getattr(
                        trade,
                        "symbol",
                        "",
                    )
                )

                if symbol == PILOT_SYMBOL:
                    count += 1

            return count

        except Exception as exc:

            logger.exception(
                "AUTO TRADER: PAPER COUNT ERROR: %s",
                exc,
            )

            return PROJECT_MAX_POSITIONS

    try:

        return get_position_count(
            PILOT_SYMBOL
        )

    except Exception as exc:

        logger.exception(
            "AUTO TRADER: LIVE COUNT ERROR: %s",
            exc,
        )

        return PROJECT_MAX_POSITIONS


def _resolve_lot(
    opportunity: dict[str, Any],
) -> float:

    raw = (
        opportunity.get("lot")
        or opportunity.get("volume")
        or DEFAULT_LOT
    )

    try:
        lot = float(raw)
    except Exception as exc:
        raise ValueError(
            "Invalid lot"
        ) from exc

    if not math.isfinite(lot):
        raise ValueError(
            "Non-finite lot"
        )

    if lot < MIN_PROJECT_LOT:
        raise ValueError(
            f"Lot below minimum: {lot}"
        )

    # HARD REJECT.
    if lot > MAX_PROJECT_LOT:
        raise ValueError(
            f"Lot above hard limit: {lot}"
        )

    return round(
        lot,
        2,
    )


def _has_existing_trade(
    symbol: str,
) -> bool:

    try:
        return (
            _get_active_trade_count() > 0
        )
    except Exception:
        return True


def execute_trade(
    opportunity: Optional[dict[str, Any]],
):

    if not opportunity:
        return None

    if not _validate_opportunity(
        opportunity
    ):
        logger.warning(
            "AUTO TRADER: INVALID OPPORTUNITY"
        )
        return None

    active_count = (
        _get_active_trade_count()
    )

    if active_count >= PROJECT_MAX_POSITIONS:

        logger.warning(
            "AUTO TRADER: POSITION LIMIT "
            "%s/%s",
            active_count,
            PROJECT_MAX_POSITIONS,
        )

        return None

    try:

        lot = _resolve_lot(
            opportunity
        )

    except ValueError as exc:

        logger.warning(
            "AUTO TRADER: LOT REJECTED: %s",
            exc,
        )

        return None

    symbol = _normalize_symbol(
        opportunity.get("symbol")
    )

    side = _normalize_signal(
        opportunity.get("signal")
        or opportunity.get("side")
        or opportunity.get("direction")
    )

    entry = float(
        opportunity.get(
            "entry_price",
            opportunity.get(
                "entry",
                opportunity.get(
                    "price"
                ),
            ),
        )
    )

    sl = float(
        opportunity.get(
            "stop_loss",
            opportunity.get(
                "sl"
            ),
        )
    )

    tp = float(
        opportunity.get(
            "take_profit",
            opportunity.get(
                "tp"
            ),
        )
    )

    confidence = float(
        opportunity.get(
            "confidence",
            0,
        )
    )

    result = open_market_position(
        symbol=symbol,
        side=side,
        lot=lot,
        sl=sl,
        tp=tp,
        confidence=confidence,
    )

    if not result:
        return None

    # --------------------------------------------------------
    # PAPER / LIVE TRADE PERSISTENCE
    # --------------------------------------------------------

    ticket = result.get("ticket")

    trade_record = {
        "ticket": ticket,
        "symbol": symbol,
        "side": side,
        "entry": result.get(
            "price",
            entry,
        ),
        "exit_price": None,
        "tp": tp,
        "sl": sl,
        "quantity": lot,
        "confidence": confidence,
        "pnl": 0,
        "status": "OPEN",
    }

    try:

        saved = save_trade(
            trade_record
        )

        if saved is not None:
            result["trade_id"] = saved

    except Exception as exc:

        # IMPORTANT:
        # The MT5 order may already exist.
        # NEVER retry the order because DB persistence failed.
        logger.exception(
            "AUTO TRADER: DATABASE SAVE FAILED: %s",
            exc,
        )

        result["database_save_failed"] = True

    return result


__all__ = [
    "execute_trade",
]
