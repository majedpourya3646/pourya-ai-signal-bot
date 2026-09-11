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

MIN_PROJECT_LOT = 0.01
MAX_PROJECT_LOT = 0.03
MAX_PROJECT_POSITIONS = 5


# ============================================================
# SAFE PROJECT LIMITS
# ============================================================

try:
    PROJECT_MAX_POSITIONS = min(
        MAX_PROJECT_POSITIONS,
        max(
            1,
            int(MAX_OPEN_TRADES),
        ),
    )
except Exception:
    PROJECT_MAX_POSITIONS = MAX_PROJECT_POSITIONS


# ============================================================
# SYMBOL
# ============================================================

def _normalize_symbol(
    symbol: Any,
) -> str:

    if symbol is None:
        return ""

    return str(
        symbol
    ).strip().upper()


def _is_xauusd_symbol(
    symbol: Any,
) -> bool:

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

    value = str(
        signal
    ).upper().strip()

    if value in (
        "BUY",
        "STRONG BUY",
    ):
        return "BUY"

    if value in (
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

    if not _is_xauusd_symbol(
        raw_symbol
    ):

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

    if confidence < float(
        MIN_CONFIDENCE
    ):

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

    PAPER:
        SQLite project records are used.

    LIVE:
        MT5 / Order Manager is the source of truth.

    Fail-closed:
        None is returned if the required source cannot be
        reliably checked.
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

                if not isinstance(
                    trade,
                    dict,
                ):
                    continue

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

            logger.error(
                "LIVE POSITION COUNT "
                "UNAVAILABLE"
            )

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
    Resolve the requested lot.

    Priority:
        opportunity["lot"]
        opportunity["volume"]
        DEFAULT_LOT

    HARD SAFETY RULE:

        0.01 <= lot <= 0.03

    A request above 0.03 is REJECTED.

    It is intentionally NOT capped down to 0.03 because
    silently modifying a risk request can hide an upstream
    risk-calculation error.
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

        # ----------------------------------------------------
        # Finite check
        # ----------------------------------------------------

        if not (
            lot == lot
            and abs(lot) != float("inf")
        ):

            logger.warning(
                f"INVALID NON-FINITE LOT={lot}"
            )

            return None

        # ----------------------------------------------------
        # Project minimum
        # ----------------------------------------------------

        if lot < MIN_PROJECT_LOT:

            logger.warning(
                "TRADE REJECTED - "
                f"LOT BELOW PROJECT MINIMUM: "
                f"{lot} < {MIN_PROJECT_LOT}"
            )

            return None

        # ----------------------------------------------------
        # HARD PROJECT CEILING
        # ----------------------------------------------------

        if lot > MAX_PROJECT_LOT:

            logger.error(
                "TRADE REJECTED - "
                f"LOT ABOVE PROJECT MAXIMUM: "
                f"{lot} > {MAX_PROJECT_LOT}"
            )

            return None

        # ----------------------------------------------------
        # Normalize expected project step
        # ----------------------------------------------------

        normalized = round(
            lot,
            2,
        )

        if normalized < MIN_PROJECT_LOT:

            return None

        if normalized > MAX_PROJECT_LOT:

            return None

        return normalized

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
    Compatibility helper.

    IMPORTANT:
    Existing XAUUSD positions do NOT automatically block a new
    trade. The actual limit is PROJECT_MAX_POSITIONS.
    """

    try:

        open_trades = get_open_trades()

        if not open_trades:
            return False

        for trade in open_trades:

            if not isinstance(
                trade,
                dict,
            ):
                continue

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

        # Fail closed for compatibility callers.
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
        # Canonical pilot symbol
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
        # Active position limit
        # ----------------------------------------------------

        active_count = (
            _get_active_trade_count()
        )

        if active_count is None:

            logger.error(
                "TRADE REJECTED - "
                "ACTIVE POSITION COUNT "
                "COULD NOT BE VERIFIED"
            )

            return None

        if active_count >= PROJECT_MAX_POSITIONS:

            logger.info(
                "TRADE REJECTED - "
                f"MAX POSITIONS "
                f"{active_count}/"
                f"{PROJECT_MAX_POSITIONS}"
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
                "INVALID PROJECT LOT"
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
            "ACTIVE_POSITIONS="
            f"{active_count}/"
            f"{PROJECT_MAX_POSITIONS}"
        )

        logger.info(
            f"PAPER_TRADING={PAPER_TRADING}"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # Central Order Manager
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
        # Status
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
            "ticket": order.get(
                "ticket"
            ),

            "deal": order.get(
                "deal"
            ),

            "symbol": symbol,

            "side": signal,

            "entry": order.get(
                "price",
                entry,
            ),

            "tp": tp,

            "sl": sl,

            "quantity": order.get(
                "volume",
                lot,
            ),

            "confidence": confidence,

            "status": status,

            "paper_trading": order.get(
                "paper_trading",
                PAPER_TRADING,
            ),
        }

        trade_id = save_trade(
            trade
        )

        # ----------------------------------------------------
        # Database failure
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
        # Success
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
            f"TICKET={trade.get('ticket')}"
        )

        logger.info(
            f"DEAL={trade.get('deal')}"
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

**نکته مهم:** این فایل فقط آماده‌ی جایگزینی است؛ من روی سیستم ویندوزی تو آن را ننوشتم. بعد از این، فایل بعدی باید **`core/order_manager.py`** باشد تا `open_market_position()` دقیقاً با همین قرارداد و با `mt5_connector.py` هماهنگ شود.
