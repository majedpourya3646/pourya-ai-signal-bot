```python
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
# XAUUSD CONFIG
# ============================================================

XAUUSD_SYMBOL = "XAUUSD.st"


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================

def _normalize_symbol(symbol: Any) -> str:
    """
    Normalize symbol only for comparison.

    Example:
        XAUUSD.st -> XAUUSD.ST
        XAUUSD.ST -> XAUUSD.ST
    """
    if symbol is None:
        return ""

    return str(symbol).strip().upper()


def _is_xauusd_symbol(symbol: Any) -> bool:
    """
    Case-insensitive XAUUSD.st validation.
    """

    return (
        _normalize_symbol(symbol)
        == _normalize_symbol(XAUUSD_SYMBOL)
    )


# ============================================================
# SIGNAL NORMALIZATION
# ============================================================

def _normalize_signal(signal: Any) -> Optional[str]:

    if signal is None:
        return None

    signal = str(signal).upper().strip()

    if signal in ("BUY", "STRONG BUY"):
        return "BUY"

    if signal in ("SELL", "STRONG SELL"):
        return "SELL"

    return None


# ============================================================
# OPPORTUNITY VALIDATION
# ============================================================

def _validate_opportunity(
    opportunity: Dict[str, Any]
) -> bool:

    if not opportunity:
        logger.info("NO OPPORTUNITY")
        return False

    # --------------------------------------------------------
    # SYMBOL
    # --------------------------------------------------------

    raw_symbol = opportunity.get("symbol", "")

    if not _is_xauusd_symbol(raw_symbol):

        logger.warning(
            f"TRADE REJECTED - "
            f"ONLY {XAUUSD_SYMBOL} ALLOWED: "
            f"{raw_symbol}"
        )

        return False

    # --------------------------------------------------------
    # SIGNAL
    # --------------------------------------------------------

    signal = _normalize_signal(
        opportunity.get("signal", "")
    )

    if signal is None:

        logger.warning(
            "INVALID SIGNAL"
        )

        return False

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    try:

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )

    except (TypeError, ValueError):

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

    # --------------------------------------------------------
    # PRICE DATA
    # --------------------------------------------------------

    entry = opportunity.get("entry")
    tp = opportunity.get("tp")
    sl = opportunity.get("sl")

    if (
        entry is None
        or tp is None
        or sl is None
    ):

        logger.error(
            "ENTRY / TP / SL MISSING"
        )

        return False

    # --------------------------------------------------------
    # PRICE CONVERSION
    # --------------------------------------------------------

    try:

        entry = float(entry)
        tp = float(tp)
        sl = float(sl)

    except (TypeError, ValueError):

        logger.error(
            "INVALID ENTRY / TP / SL"
        )

        return False

    # --------------------------------------------------------
    # PRICE VALIDATION
    # --------------------------------------------------------

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
# EXISTING DATABASE TRADE CHECK
# ============================================================

def _has_existing_trade() -> bool:

    try:

        open_trades = get_open_trades()

        if not open_trades:
            return False

        for trade in open_trades:

            symbol = trade.get(
                "symbol",
                ""
            )

            status = str(
                trade.get(
                    "status",
                    ""
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
        # if database status is uncertain,
        # DO NOT open another trade.

        return True


# ============================================================
# EXECUTE TRADE
# ============================================================

def execute_trade(
    opportunity: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    try:

        # ----------------------------------------------------
        # VALIDATE OPPORTUNITY
        # ----------------------------------------------------

        if not _validate_opportunity(
            opportunity
        ):

            return None

        # ----------------------------------------------------
        # CANONICAL SYMBOL
        # ----------------------------------------------------
        #
        # IMPORTANT:
        # Never pass the uppercased comparison value
        # XAUUSD.ST to MT5.
        #
        # Always use the exact broker symbol:
        # XAUUSD.st
        #

        symbol = XAUUSD_SYMBOL

        # ----------------------------------------------------
        # SIGNAL
        # ----------------------------------------------------

        signal = _normalize_signal(
            opportunity.get("signal")
        )

        # ----------------------------------------------------
        # NUMERIC VALUES
        # ----------------------------------------------------

        confidence = float(
            opportunity.get(
                "confidence",
                0
            )
        )

        entry = float(
            opportunity.get("entry")
        )

        tp = float(
            opportunity.get("tp")
        )

        sl = float(
            opportunity.get("sl")
        )

        # ----------------------------------------------------
        # DATABASE OPEN TRADE CHECK
        # ----------------------------------------------------

        if _has_existing_trade():

            logger.info(
                "TRADE REJECTED - "
                "XAUUSD OPEN TRADE EXISTS"
            )

            return None

        # ----------------------------------------------------
        # MT5 POSITION COUNT
        # ----------------------------------------------------

        try:

            current_positions = (
                get_position_count()
            )

            if (
                current_positions
                >= MAX_OPEN_TRADES
            ):

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
        # MT5 EXISTING POSITION CHECK
        # ----------------------------------------------------

        if has_open_position(
            symbol
        ):

            logger.info(
                f"TRADE REJECTED - "
                f"MT5 POSITION EXISTS "
                f"{symbol}"
            )

            return None

        # ----------------------------------------------------
        # LOT
        # ----------------------------------------------------

        lot = DEFAULT_LOT

        # ----------------------------------------------------
        # DECISION LOG
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
            "================================"
        )

        # ----------------------------------------------------
        # OPEN MARKET POSITION
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

        # ----------------------------------------------------
        # ORDER FAILURE
        # ----------------------------------------------------

        if not order:

            logger.error(
                f"ORDER MANAGER REJECTED "
                f"{symbol} {signal}"
            )

            return None

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if order.get(
            "paper_trading",
            False
        ):

            status = "PAPER_OPEN"

        else:

            status = "OPEN"

        # ----------------------------------------------------
        # TRADE OBJECT
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

            "paper_trading": order.get(
                "paper_trading",
                PAPER_TRADING
            ),
        }

        # ----------------------------------------------------
        # DATABASE SAVE
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
        # SUCCESS LOG
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
            "================================"
        )

        return trade

    except Exception as exc:

        logger.exception(
            f"AUTO TRADER ERROR {exc}"
        )

        return None
```
