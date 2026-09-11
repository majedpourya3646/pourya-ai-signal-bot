```python
# core/opportunity_engine.py

from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols
)

from core.trade_manager import (
    get_open_trades
)

from core.order_manager import (
    get_position_count,
    has_open_position
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)


# ============================================================
# Configuration
# ============================================================

XAUUSD_SYMBOL = "XAUUSD.st"
XAUUSD_SYMBOL_NORMALIZED = XAUUSD_SYMBOL.upper()


# ============================================================
# Helpers
# ============================================================

def _normalize_symbol(symbol):
    """
    Normalize broker symbol names for reliable comparison.

    Example:
        XAUUSD.st -> XAUUSD.ST
        XAUUSD.ST -> XAUUSD.ST
    """
    try:
        if symbol is None:
            return ""

        return str(symbol).strip().upper()

    except Exception:
        return ""


def _normalize_signal(signal):
    """
    Normalize BUY / SELL signal names.
    """
    try:
        if signal is None:
            return ""

        return str(signal).strip().upper()

    except Exception:
        return ""


def _calculate_risk_reward(entry, sl, tp):
    """
    Calculate risk/reward ratio safely.
    """
    try:
        entry = float(entry)
        sl = float(sl)
        tp = float(tp)

        risk = abs(entry - sl)
        reward = abs(tp - entry)

        if risk <= 0:
            return 0.0

        return reward / risk

    except (
        TypeError,
        ValueError,
        ZeroDivisionError
    ):
        return 0.0


# ============================================================
# Calculate Opportunity Score
# ============================================================

def calculate_opportunity_score(item):

    try:

        if not item:
            return 0

        score = 0

        confidence = float(
            item.get(
                "confidence",
                0
            )
        )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        if confidence >= 80:

            score += 40

        elif confidence >= 70:

            score += 30

        elif confidence >= MIN_CONFIDENCE:

            score += 20

        else:

            logger.info(
                f"OPPORTUNITY SCORE REJECTED | "
                f"CONFIDENCE={confidence} "
                f"< MIN_CONFIDENCE={MIN_CONFIDENCE}"
            )

            return 0

        # ----------------------------------------------------
        # Signal
        # ----------------------------------------------------

        signal = _normalize_signal(
            item.get(
                "signal",
                ""
            )
        )

        if signal not in (
            "BUY",
            "SELL"
        ):

            logger.info(
                f"OPPORTUNITY SCORE REJECTED | "
                f"INVALID SIGNAL={signal}"
            )

            return 0

        score += 20

        # ----------------------------------------------------
        # Multi Timeframe
        # ----------------------------------------------------

        timeframes = item.get(
            "timeframes",
            {}
        )

        if (
            isinstance(timeframes, dict)
            and len(timeframes) >= 3
        ):

            score += 20

        # ----------------------------------------------------
        # Entry / TP / SL / Risk Reward
        # ----------------------------------------------------

        entry = item.get("entry")
        tp = item.get("tp")
        sl = item.get("sl")

        if (
            entry is not None
            and tp is not None
            and sl is not None
        ):

            rr = _calculate_risk_reward(
                entry,
                sl,
                tp
            )

            if rr >= 2.0:

                score += 20

            elif rr >= 1.5:

                score += 10

        logger.info(
            f"OPPORTUNITY SCORE | "
            f"SIGNAL={signal} | "
            f"CONFIDENCE={confidence} | "
            f"SCORE={score}"
        )

        return score

    except Exception as exc:

        logger.exception(
            f"OPPORTUNITY SCORE ERROR {exc}"
        )

        return 0


# ============================================================
# Validate Opportunity
# ============================================================

def validate_opportunity(item):

    try:

        if not item:

            logger.info(
                "REJECTED OPPORTUNITY | EMPTY ITEM"
            )

            return False

        symbol = _normalize_symbol(
            item.get(
                "symbol",
                ""
            )
        )

        signal = _normalize_signal(
            item.get(
                "signal",
                ""
            )
        )

        try:

            confidence = float(
                item.get(
                    "confidence",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            logger.info(
                f"REJECTED {symbol} | "
                "INVALID CONFIDENCE"
            )

            return False

        entry = item.get("entry")
        tp = item.get("tp")
        sl = item.get("sl")

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if symbol != XAUUSD_SYMBOL_NORMALIZED:

            logger.info(
                f"REJECTED {symbol} | "
                f"ONLY {XAUUSD_SYMBOL}"
            )

            return False

        # ----------------------------------------------------
        # Signal
        # ----------------------------------------------------

        if signal not in (
            "BUY",
            "SELL"
        ):

            logger.info(
                f"REJECTED {symbol} | "
                f"INVALID SIGNAL={signal}"
            )

            return False

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        if confidence < MIN_CONFIDENCE:

            logger.info(
                f"REJECTED {symbol} | "
                f"LOW CONFIDENCE={confidence:.2f} "
                f"< MIN_CONFIDENCE={MIN_CONFIDENCE}"
            )

            return False

        # ----------------------------------------------------
        # Prices
        # ----------------------------------------------------

        if (
            entry is None
            or tp is None
            or sl is None
        ):

            logger.info(
                f"REJECTED {symbol} | "
                "MISSING ENTRY/TP/SL"
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

            logger.info(
                f"REJECTED {symbol} | "
                "INVALID PRICE DATA"
            )

            return False

        # ----------------------------------------------------
        # Positive prices
        # ----------------------------------------------------

        if (
            entry <= 0
            or tp <= 0
            or sl <= 0
        ):

            logger.info(
                f"REJECTED {symbol} | "
                "NON-POSITIVE PRICE"
            )

            return False

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if signal == "BUY":

            if tp <= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    f"INVALID BUY TP={tp} "
                    f"ENTRY={entry}"
                )

                return False

            if sl >= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    f"INVALID BUY SL={sl} "
                    f"ENTRY={entry}"
                )

                return False

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        if signal == "SELL":

            if tp >= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    f"INVALID SELL TP={tp} "
                    f"ENTRY={entry}"
                )

                return False

            if sl <= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    f"INVALID SELL SL={sl} "
                    f"ENTRY={entry}"
                )

                return False

        # ----------------------------------------------------
        # Risk / Reward
        # ----------------------------------------------------

        rr = _calculate_risk_reward(
            entry,
            sl,
            tp
        )

        if rr <= 0:

            logger.info(
                f"REJECTED {symbol} | "
                "ZERO RISK"
            )

            return False

        if rr < 1.5:

            logger.info(
                f"REJECTED {symbol} | "
                f"LOW RISK REWARD={rr:.2f}"
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            f"OPPORTUNITY VALIDATION ERROR {exc}"
        )

        return False


# ============================================================
# Check Duplicate Trade
# ============================================================

def has_open_trade(
    symbol
):

    try:

        symbol = _normalize_symbol(
            symbol
        )

        if not symbol:

            return True

        # ----------------------------------------------------
        # Database
        # ----------------------------------------------------

        open_trades = get_open_trades()

        if open_trades:

            for trade in open_trades:

                if not isinstance(
                    trade,
                    dict
                ):

                    continue

                trade_symbol = _normalize_symbol(
                    trade.get(
                        "symbol",
                        ""
                    )
                )

                status = str(
                    trade.get(
                        "status",
                        ""
                    )
                ).upper().strip()

                if (
                    trade_symbol == symbol
                    and status in (
                        "OPEN",
                        "PAPER_OPEN",
                        "ACTIVE",
                    )
                ):

                    logger.info(
                        f"DUPLICATE TRADE | "
                        f"{symbol} | "
                        f"STATUS={status}"
                    )

                    return True

        # ----------------------------------------------------
        # MT5
        # ----------------------------------------------------

        if has_open_position(
            symbol
        ):

            logger.info(
                f"DUPLICATE MT5 POSITION | "
                f"{symbol}"
            )

            return True

        return False

    except Exception as exc:

        logger.error(
            f"DUPLICATE TRADE CHECK ERROR "
            f"{symbol} {exc}"
        )

        # Fail-safe
        return True


# ============================================================
# Scan Opportunities
# ============================================================

def scan_opportunities():

    try:

        # ----------------------------------------------------
        # Position limit
        # ----------------------------------------------------

        position_count = get_position_count()

        if position_count < 0:

            logger.error(
                "POSITION COUNT UNAVAILABLE | "
                "SCAN BLOCKED"
            )

            return []

        if position_count >= MAX_OPEN_TRADES:

            logger.info(
                f"MAX MT5 POSITIONS REACHED "
                f"{position_count}/"
                f"{MAX_OPEN_TRADES}"
            )

            return []

        # ----------------------------------------------------
        # Database open trades
        # ----------------------------------------------------

        open_trades = get_open_trades()

        if open_trades is None:

            open_trades = []

        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(
                f"MAX OPEN TRADES REACHED "
                f"{len(open_trades_
```
