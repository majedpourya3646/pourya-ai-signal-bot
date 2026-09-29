# core/auto_trader.py

from typing import Optional, Dict, Any

from core.logger import logger

from core.order_manager import (
    open_market_position,
    get_position_count,
)

from core.trade_manager import (
    save_trade,
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES,
    DEFAULT_LOT,
    PAPER_TRADING,
    PILOT_SYMBOL,
    MT5_ORDER_COMMENT,
)


# ============================================================
# Configuration
# ============================================================

XAUUSD_SYMBOL = str(
    PILOT_SYMBOL
).strip()

XAUUSD_SYMBOL_NORMALIZED = XAUUSD_SYMBOL.upper()


# ============================================================
# Symbol Helpers
# ============================================================

def _normalize_symbol(
    symbol: Any
) -> str:

    if symbol is None:

        return ""

    return str(
        symbol
    ).strip().upper()


def _is_xauusd_symbol(
    symbol: Any
) -> bool:

    return (
        _normalize_symbol(symbol)
        == XAUUSD_SYMBOL_NORMALIZED
    )


# ============================================================
# Signal Helpers
# ============================================================

def _normalize_signal(
    signal: Any
) -> Optional[str]:

    if signal is None:

        return None

    signal = str(
        signal
    ).upper().strip()

    if signal in (
        "BUY",
        "STRONG BUY"
    ):

        return "BUY"

    if signal in (
        "SELL",
        "STRONG SELL"
    ):

        return "SELL"

    return None


# ============================================================
# Opportunity Validation
# ============================================================

def _validate_opportunity(
    opportunity: Dict[str, Any]
) -> bool:

    if not opportunity:

        logger.info(
            "NO OPPORTUNITY"
        )

        return False

    raw_symbol = opportunity.get(
        "symbol",
        ""
    )

    if not _is_xauusd_symbol(
        raw_symbol
    ):

        logger.warning(
            f"TRADE REJECTED - ONLY "
            f"{XAUUSD_SYMBOL} ALLOWED: "
            f"{raw_symbol}"
        )

        return False

    signal = _normalize_signal(
        opportunity.get(
            "signal",
            ""
        )
    )

    if signal is None:

        logger.warning(
            "INVALID SIGNAL"
        )

        return False

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        logger.warning(
            "INVALID CONFIDENCE"
        )

        return False

    if confidence < MIN_CONFIDENCE:

        logger.info(
            f"TRADE REJECTED - "
            f"LOW CONFIDENCE={confidence} "
            f"MIN={MIN_CONFIDENCE}"
        )

        return False

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
        ValueError
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
            f"INVALID PRICE VALUES "
            f"ENTRY={entry} "
            f"SL={sl} "
            f"TP={tp}"
        )

        return False

    # --------------------------------------------------------
    # Price structure
    # --------------------------------------------------------

    if signal == "BUY":

        if not (
            sl < entry < tp
        ):

            logger.warning(
                "TRADE REJECTED - "
                "INVALID BUY PRICE STRUCTURE"
            )

            return False

    elif signal == "SELL":

        if not (
            tp < entry < sl
        ):

            logger.warning(
                "TRADE REJECTED - "
                "INVALID SELL PRICE STRUCTURE"
            )

            return False

    return True


# ============================================================
# Execute Trade
# ============================================================

def execute_trade(
    opportunity: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    try:

        # ----------------------------------------------------
        # Validate opportunity
        # ----------------------------------------------------

        if not _validate_opportunity(
            opportunity
        ):

            return None

        # ----------------------------------------------------
        # Normalize symbol
        # ----------------------------------------------------

        symbol = XAUUSD_SYMBOL

        # ----------------------------------------------------
        # Normalize signal
        # ----------------------------------------------------

        signal = _normalize_signal(
            opportunity.get(
                "signal"
            )
        )

        if signal is None:

            logger.warning(
                "TRADE REJECTED - "
                "INVALID SIGNAL"
            )

            return None

        # ----------------------------------------------------
        # Values
        # ----------------------------------------------------

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )

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
        # Position capacity
        #
        # Do NOT block merely because an XAUUSD position
        # already exists.
        #
        # The final position-limit and safety validation
        # remains inside order_manager / connector.
        # ----------------------------------------------------

        try:

            current_positions = get_position_count()

            if current_positions >= MAX_OPEN_TRADES:

                logger.info(
                    f"TRADE REJECTED - "
                    f"MAX POSITIONS "
                    f"{current_positions}/"
                    f"{MAX_OPEN_TRADES}"
                )

                return None

        except Exception as exc:

            logger.exception(
                f"POSITION COUNT ERROR {exc}"
            )

            return None

        # ----------------------------------------------------
        # Lot
        # ----------------------------------------------------

        lot = DEFAULT_LOT

        # ----------------------------------------------------
        # Decision Log
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
            f"PAPER_TRADING={PAPER_TRADING}"
        )

        logger.info(
            f"OPEN_POSITIONS="
            f"{current_positions}/"
            f"{MAX_OPEN_TRADES}"
        )

        logger.info(
            "================================"
        )

        # ----------------------------------------------------
        # Open position
        #
        # order_manager remains the final safety gate.
        # ----------------------------------------------------

        order = open_market_position(
            symbol=symbol,
            side=signal,
            lot=lot,
            sl=sl,
            tp=tp,
            confidence=confidence,
            comment=MT5_ORDER_COMMENT,
        )

        if not order:

            logger.error(
                f"ORDER MANAGER REJECTED "
                f"{symbol} {signal}"
            )

            return None

        # ----------------------------------------------------
        # Trade status
        #
        # Paper trades must also use OPEN because
        # paper_position_manager monitors OPEN trades.
        # The paper/live distinction is stored separately.
        # ----------------------------------------------------

        is_paper = bool(
            order.get(
                "paper_trading",
                PAPER_TRADING
            )
        )

        status = "OPEN"

        # ----------------------------------------------------
        # Build trade record
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
                entry
            ),
            "tp": tp,
            "sl": sl,
            "quantity": order.get(
                "volume",
                lot
            ),
            "confidence": confidence,
            "status": status,
            "paper_trading": is_paper,
        }

        # ----------------------------------------------------
        # Save trade
        # ----------------------------------------------------

        trade_id = save_trade(
            trade
        )

        if trade_id is None:

            logger.error(
                "TRADE DATABASE SAVE FAILED"
            )

            return None

        trade["id"] = trade_id

        # ----------------------------------------------------
        # Success Log
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
            f"STATUS={status}"
        )

        logger.info(
            f"PAPER_TRADING={is_paper}"
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

