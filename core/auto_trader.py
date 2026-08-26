# core/auto_trader.py

from typing import Optional, Dict, Any

from core.logger import logger

from core.order_manager import (
    open_market_position,
    get_position_count,
    has_open_position,
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
# Configuration
# ============================================================

XAUUSD_SYMBOL = "XAUUSD.st"


# ============================================================
# Helpers
# ============================================================

def _normalize_signal(
    signal: str
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
# Validate Opportunity
# ============================================================

def _validate_opportunity(
    opportunity: Dict[str, Any]
) -> bool:

    if not opportunity:
        logger.info(
            "NO OPPORTUNITY"
        )
        return False

    symbol = str(
        opportunity.get(
            "symbol",
            ""
        )
    ).upper().strip()

    if symbol != XAUUSD_SYMBOL:

        logger.warning(
            f"TRADE REJECTED - "
            f"ONLY {XAUUSD_SYMBOL} ALLOWED: "
            f"{symbol}"
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

    return True


# ============================================================
# Check Existing Trades
# ============================================================

def _has_existing_trade() -> bool:

    try:

        open_trades = get_open_trades()

        if not open_trades:

            return False

        for trade in open_trades:

            symbol = str(
                trade.get(
                    "symbol",
                    ""
                )
            ).upper().strip()

            status = str(
                trade.get(
                    "status",
                    ""
                )
            ).upper().strip()

            if (
                symbol == XAUUSD_SYMBOL
                and status in (
                    "OPEN",
                    "PAPER_OPEN",
                    "ACTIVE",
                )
            ):

                logger.info(
                    "XAUUSD TRADE ALREADY EXISTS"
                )

                return True

        return False

    except Exception as exc:

        logger.exception(
            f"TRADE CHECK ERROR {exc}"
        )

        # Fail-safe:
        # if database cannot be checked,
        # do not open a new trade.
        return True


# ============================================================
# Execute Trade
# ============================================================

def execute_trade(
    opportunity: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    try:

        # ====================================================
        # Basic validation
        # ====================================================

        if not _validate_opportunity(
            opportunity
        ):

            return None

        # ====================================================
        # Data
        # ====================================================

        symbol = str(
            opportunity.get(
                "symbol"
            )
        ).upper().strip()

        signal = _normalize_signal(
            opportunity.get(
                "signal"
            )
        )

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

        # ====================================================
        # Open trade database check
        # ====================================================

        if _has_existing_trade():

            logger.info(
                "TRADE REJECTED - "
                "XAUUSD OPEN TRADE EXISTS"
            )

            return None

        # ====================================================
        # MT5 position check
        # ====================================================

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

        if has_open_position(
            symbol
        ):

            logger.info(
                f"TRADE REJECTED - "
                f"MT5 POSITION EXISTS "
                f"{symbol}"
            )

            return None

        # ====================================================
        # Lot
        # ====================================================

        lot = DEFAULT_LOT

        # ====================================================
        # Log decision
        # ====================================================

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
            "================================"
        )

        # ====================================================
        # Send order through Order Manager
        # ====================================================

        # IMPORTANT:
        # Order Manager decides whether this is
        # Paper Trading or Real Trading.

        order = open_market_position(

            symbol=symbol,

            side=signal,

            lot=lot,

            sl=sl,

            tp=tp,

            confidence=confidence,

            comment="Pourya Trader AI"

        )

        if not order:

            logger.error(
                f"ORDER MANAGER REJECTED "
                f"{symbol} {signal}"
            )

            return None

        # ====================================================
        # Determine status
        # ====================================================

        if order.get(
            "paper_trading",
            False
        ):

            status = "PAPER_OPEN"

        else:

            status = "OPEN"

        # ====================================================
        # Build trade
        # ====================================================

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
                    entry
                ),

            "tp":
                tp,

            "sl":
                sl,

            "quantity":
                order.get(
                    "volume",
                    lot
                ),

            "confidence":
                confidence,

            "status":
                status,

            "paper_trading":
                order.get(
                    "paper_trading",
                    PAPER_TRADING
                ),

        }

        # ====================================================
        # Save trade
        # ====================================================

        trade_id = save_trade(
            trade
        )

        if trade_id is None:

            logger.error(
                "TRADE DATABASE SAVE FAILED"
            )

            # IMPORTANT:
            # If a real MT5 order was already opened
            # but DB save failed, we do not automatically
            # open another order.
            return None

        trade["id"] = trade_id

        # ====================================================
        # Final log
        # ====================================================

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
            "================================"
        )

        return trade

    except Exception as exc:

        logger.exception(
            f"AUTO TRADER ERROR {exc}"
        )

        return None
