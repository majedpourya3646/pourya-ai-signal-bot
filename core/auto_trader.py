```python
from __future__ import annotations

from typing import Optional, Dict, Any

from core.logger import logger

from core.order_manager import (
    open_market_position,
    get_position_count,
)

from core.trade_manager import (
    save_trade,
    get_open_trades,
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES,
    DEFAULT_LOT,
    PAPER_TRADING,
)


# ============================================================
# PILOT CONFIG
# ============================================================

XAUUSD_SYMBOL = "XAUUSD.su"

# Hard project-level lot ceiling.
MAX_PROJECT_LOT = 0.03

# Minimum allowed project lot for the current broker/test.
MIN_PROJECT_LOT = 0.01


# ============================================================
# SYMBOL
# ============================================================

def _normalize_symbol(symbol: Any) -> str:

    if symbol is None:
        return ""

    return str(symbol).strip().upper()


def _is_xauusd_symbol(symbol: Any) -> bool:

    return (
        _normalize_symbol(symbol)
        == _normalize_symbol(XAUUSD_SYMBOL)
    )


# ============================================================
# SIGNAL
# ============================================================

def _normalize_signal(
    signal: Any,
) -> Optional[str]:

    if signal is None:
        return None

    signal = str(
        signal
    ).upper().strip()

    if signal in (
        "BUY",
        "STRONG BUY",
    ):
        return "BUY"

    if signal in (
        "SELL",
        "STRONG SELL",
    ):
        return "SELL"

    return None


# ============================================================
# OPPORTUNITY VALIDATION
# ============================================================

def _validate_opportunity(
    opportunity: Optional[Dict[str, Any]],
) -> bool:

    if not opportunity:

        logger.info(
            "NO OPPORTUNITY"
        )

        return False

    # --------------------------------------------------------
    # Symbol
    # --------------------------------------------------------

    raw_symbol = opportunity.get(
        "symbol",
        "",
    )

    if not _is_xauusd_symbol(raw_symbol):

        logger.warning(
            "TRADE REJECTED - "
            f"ONLY {XAUUSD_SYMBOL} ALLOWED: "
            f"{raw_symbol}"
        )

        return False

    # --------------------------------------------------------
    # Signal
    # --------------------------------------------------------

    signal = _normalize_signal(
        opportunity.get(
            "signal",
            "",
        )
    )

    if signal is None:

        logger.warning(
            "INVALID SIGNAL"
        )

        return False

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        logger.warning(
            "INVALID CONFIDENCE"
        )

        return False

    if confidence < MIN_CONFIDENCE:

        logger.info(
            "TRADE REJECTED - "
            f"LOW CONFIDENCE={confidence} "
            f"MIN={MIN_CONFIDENCE}"
        )

        return False

    # --------------------------------------------------------
    # Prices
    # --------------------------------------------------------

    entry = opportunity.get(
        "entry"
    )

    tp = opportunity.get(
        "tp"
    )

    sl = opportunity.get(
        "sl"
    )

    if (
        entry is None
        or tp is None
        or sl is None
    ):

        logger.error(
            "ENTRY / TP / SL MISSING"
        )

        return False

    try:

        entry = float(entry)
        tp = float(tp)
        sl = float(sl)

    except (
        TypeError,
        ValueError,
    ):

        logger.error(
            "INVALID ENTRY / TP / SL"
        )

        return False

    if (
        entry <= 0
        or tp <= 0
        or sl <= 0
    ):

        logger.error(
            "INVALID PRICE VALUES "
            f"ENTRY={entry} "
            f"SL={sl} "
            f"TP={tp}"
        )

        return False

    # --------------------------------------------------------
    # Direction validation
    # --------------------------------------------------------

    if signal == "BUY":

        if not (
            sl < entry < tp
        ):

            logger.warning(
                "TRADE REJECTED - "
                "INVALID BUY SL/TP DIRECTION"
            )

            return False

    elif signal == "SELL":

        if not (
            tp < entry < sl
        ):

            logger.warning(
                "TRADE REJECTED - "
                "INVALID SELL SL/TP DIRECTION"
            )

            return False

    return True


# ============================================================
# ACTIVE TRADE COUNT
# ============================================================

def _get_active_trade_count() -> Optional[int]:
    """
    Determine active project trades.

    Live mode:
        MT5 position count is the primary source of truth.

    Paper mode:
        SQLite OPEN/PAPER_OPEN/ACTIVE records are used because
        paper trades do not exist as MT5 positions.

    Fail-closed:
        Return None if the required source cannot be checked.
    """

    try:

        # ----------------------------------------------------
        # PAPER MODE
        # ----------------------------------------------------

        if PAPER_TRADING:

            open_trades = get_open_trades()

            if open_trades is None:

                logger.error(
                    "ACTIVE TRADE COUNT "
                    "UNAVAILABLE IN PAPER MODE"
                )

                return None

            count = 0

            for trade in open_trades:

                symbol = trade.get(
                    "symbol",
                    "",
                )

                status = str(
                    trade.get(
                        "status",
                        "",
                    )
                ).upper().strip()

                if (
                    _is_xauusd_symbol(symbol)
                    and status in (
                        "OPEN",
                        "PAPER_OPEN",
                        "ACTIVE",
                    )
                ):

                    count += 1

            return count

        # ----------------------------------------------------
        # LIVE MODE
        # ----------------------------------------------------

        current_positions = get_position_count()

        if current_positions is None:
            return None

        return int(
            current_positions
        )

    except Exception as exc:

        logger.exception(
            "ACTIVE TRADE COUNT ERROR "
            f"{exc}"
        )

        return None


# ============================================================
# LOT
# ============================================================

def _resolve_lot(
    opportunity: Dict[str, Any],
) -> Optional[float]:
    """
    Resolve requested lot.

    Priority:
        opportunity["lot"]
        opportunity["volume"]
        DEFAULT_LOT

    The result is always constrained to:

        0.01 <= lot <= 0.03

    The lower/upper broker validation is ultimately performed
    again by Order Manager / MT5 Connector.
    """

    try:

        requested = opportunity.get(
            "lot"
        )

        if requested is None:

            requested = opportunity.get(
                "volume"
            )

        if requested is None:

            requested = DEFAULT_LOT

        lot = float(
            requested
        )

        if lot <= 0:

            logger.warning(
                f"INVALID LOT={lot}"
            )

            return None

        # ----------------------------------------------------
        # Hard project ceiling
        # ----------------------------------------------------

        if lot > MAX_PROJECT_LOT:

            logger.warning(
                "LOT CAPPED BY PROJECT LIMIT "
                f"{lot} -> {MAX_PROJECT_LOT}"
            )

            lot = MAX_PROJECT_LOT

        # ----------------------------------------------------
        # Minimum project lot
        # ----------------------------------------------------

        if lot < MIN_PROJECT_LOT:

            logger.warning(
                "LOT BELOW PROJECT MINIMUM "
                f"{lot} -> {MIN_PROJECT_LOT}"
            )

            lot = MIN_PROJECT_LOT

        # ----------------------------------------------------
        # Normalize to 0.01 broker/project step
        # ----------------------------------------------------

        lot = round(
            lot,
            2,
        )

        if lot < MIN_PROJECT_LOT:
            return None

        if lot > MAX_PROJECT_LOT:
            return None

        return lot

    except (
        TypeError,
        ValueError,
    ):

        logger.warning(
            "INVALID LOT VALUE"
        )

        return None


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

def _has_existing_trade() -> bool:
    """
    Compatibility helper retained for older callers.

    IMPORTANT:
    This function no longer means "block all new trades".

    It only reports whether at least one active XAUUSD trade
    exists. The actual decision is made using MAX_OPEN_TRADES.
    """

    try:

        open_trades = get_open_trades()

        if not open_trades:
            return False

        for trade in open_trades:

            symbol = trade.get(
                "symbol",
                "",
            )

            status = str(
                trade.get(
                    "status",
                    "",
                )
            ).upper().strip()

            if (
                _is_xauusd_symbol(symbol)
                and status in (
                    "OPEN",
                    "PAPER_OPEN",
                    "ACTIVE",
                )
            ):

                return True

        return False

    except Exception as exc:

        logger.exception(
            f"TRADE CHECK ERROR {exc}"
        )

        # Fail closed for safety.
        return True


# ============================================================
# EXECUTE TRADE
# ============================================================

def execute_trade(
    opportunity: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:

    try:

        # ----------------------------------------------------
        # Opportunity validation
        # ----------------------------------------------------

        if not _validate_opportunity(
            opportunity
        ):

            return None

        # ----------------------------------------------------
        # Canonical symbol
        # ----------------------------------------------------

        symbol = XAUUSD_SYMBOL

        # ----------------------------------------------------
        # Signal
        # ----------------------------------------------------

        signal = _normalize_signal(
            opportunity.get(
                "signal"
            )
        )

        if signal is None:
            return None

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = float(
            opportunity.get(
                "confidence",
                0,
            )
        )

        # ----------------------------------------------------
        # Prices
        # ----------------------------------------------------

        entry = float(
            opportunity.get(
                "entry"
            )
        )

        tp = float(
            opportunity.get(
                "tp"
            )
        )

        sl = float(
            opportunity.get(
                "sl"
            )
        )

        # ----------------------------------------------------
        # ACTIVE POSITION LIMIT
        #
        # IMPORTANT:
        # We intentionally DO NOT reject merely because an
        # XAUUSD position already exists.
        #
        # The pilot allows up to MAX_OPEN_TRADES positions.
        # ----------------------------------------------------

        active_count = _get_active_trade_count()

        if active_count is None:

            logger.error(
                "TRADE REJECTED - "
                "ACTIVE POSITION COUNT "
                "COULD NOT BE VERIFIED"
            )

            return None

        if active_count >= MAX_OPEN_TRADES:

            logger.info(
                "TRADE REJECTED - "
                f"MAX POSITIONS "
                f"{active_count}/"
                f"{MAX_OPEN_TRADES}"
            )

            return None

        # ----------------------------------------------------
        # Resolve lot
        # ----------------------------------------------------

        lot = _resolve_lot(
            opportunity
        )

        if lot is None:

            logger.error(
                "TRADE REJECTED - "
                "INVALID LOT"
            )

            return None

        # ----------------------------------------------------
        # Decision log
        # ----------------------------------------------------

        logger.info(
            "================================"
        )

        logger.info(
            "AUTO TRADER DECISION"
        )

        logger.info(
            f"SYMBOL={symbol}"
        )

        logger.info(
            f"SIGNAL={signal}"
        )

        logger.info(
            f"CONFIDENCE={confidence}"
        )

        logger.info(
            f"ENTRY={entry}"
        )

        logger.info(
            f"SL={sl}"
        )

        logger.info(
            f"TP={tp}"
        )

        logger.info(
            f"LOT={lot}"
        )

        logger.info(
            f"ACTIVE_POSITIONS="
            f"{active_count}/"
            f"{MAX_OPEN_TRADES}"
        )

        logger.info(
            f"PAPER_TRADING="
            f"{PAPER_TRADING}"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # Order Manager
        # ----------------------------------------------------

        order = open_market_position(
            symbol=symbol,
            side=signal,
            lot=lot,
            sl=sl,
            tp=tp,
            confidence=confidence,
            comment="Pourya Trader AI",
        )

        if not order:

            logger.error(
                "ORDER MANAGER REJECTED "
                f"{symbol} {signal}"
            )

            return None

        # ----------------------------------------------------
        # Determine status
        # ----------------------------------------------------

        if order.get(
            "paper_trading",
            False,
        ):

            status = "PAPER_OPEN"

        else:

            status = "OPEN"

        # ----------------------------------------------------
        # Persist trade
        # ----------------------------------------------------

        trade = {

            "ticket":
                order.get(
                    "ticket"
                ),

            "deal":
                order.get(
                    "deal"
                ),

            "symbol":
                symbol,

            "side":
                signal,

            "entry":
                order.get(
                    "price",
                    entry,
                ),

            "tp":
                tp,

            "sl":
                sl,

            "quantity":
                order.get(
                    "volume",
                    lot,
                ),

            "confidence":
                confidence,

            "status":
                status,

            "paper_trading":
                order.get(
                    "paper_trading",
                    PAPER_TRADING,
                ),
        }

        trade_id = save_trade(
            trade
        )

        # ----------------------------------------------------
        # Database failure handling
        #
        # IMPORTANT:
        # If an order was already accepted by MT5 but the DB
        # save fails, DO NOT retry the order.
        # ----------------------------------------------------

        if trade_id is None:

            logger.error(
                "TRADE DATABASE SAVE FAILED "
                "- ORDER WILL NOT BE RETRIED"
            )

            trade["database_save_failed"] = True

            return trade

        trade["id"] = trade_id

        # ----------------------------------------------------
        # Success log
        # ----------------------------------------------------

        logger.info(
            "================================"
        )

        logger.info(
            "TRADE EXECUTED SUCCESSFULLY"
        )

        logger.info(
            f"ID={trade_id}"
        )

        logger.info(
            f"SYMBOL={symbol}"
        )

        logger.info(
            f"SIDE={signal}"
        )

        logger.info(
            f"ENTRY={trade.get('entry')}"
        )

        logger.info(
            f"SL={sl}"
        )

        logger.info(
            f"TP={tp}"
        )

        logger.info(
            f"LOT={trade.get('quantity')}"
        )

        logger.info(
            f"STATUS={status}"
        )

        logger.info(
            "================================"
        )

        return trade

    except Exception as exc:

        logger.exception(
            f"AUTO TRADER ERROR {exc}"
        )

        return None


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "execute_trade",
    "_normalize_symbol",
    "_is_xauusd_symbol",
    "_normalize_signal",
]
```
