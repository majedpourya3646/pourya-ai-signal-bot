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
    Normalize broker symbol names for safe comparison.

    Example:
        XAUUSD.st -> XAUUSD.ST
        xauusd.ST -> XAUUSD.ST
    """

    return str(
        symbol or ""
    ).upper().strip()


def _normalize_signal(signal):
    """
    Normalize BUY / SELL signal.
    """

    return str(
        signal or ""
    ).upper().strip()


def _calculate_risk_reward(
    entry,
    tp,
    sl
):
    """
    Calculate risk/reward ratio safely.
    """

    try:

        entry = float(entry)
        tp = float(tp)
        sl = float(sl)

        risk = abs(
            entry - sl
        )

        reward = abs(
            tp - entry
        )

        if risk <= 0:

            return 0.0

        return reward / risk

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# ============================================================
# Calculate Opportunity Score
# ============================================================

def calculate_opportunity_score(item):

    try:

        if not isinstance(
            item,
            dict
        ):

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
                f"LOW CONFIDENCE | "
                f"CONFIDENCE={confidence} | "
                f"MIN={MIN_CONFIDENCE}"
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
                f"INVALID SIGNAL | "
                f"SIGNAL={signal}"
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
            isinstance(
                timeframes,
                dict
            )
            and len(timeframes) >= 3
        ):

            score += 20

        # ----------------------------------------------------
        # Entry / TP / SL
        # ----------------------------------------------------

        entry = item.get(
            "entry"
        )

        tp = item.get(
            "tp"
        )

        sl = item.get(
            "sl"
        )

        if (
            entry is not None
            and tp is not None
            and sl is not None
        ):

            rr = _calculate_risk_reward(
                entry,
                tp,
                sl
            )

            if rr >= 2:

                score += 20

            elif rr >= 1.5:

                score += 10

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

        if not isinstance(
            item,
            dict
        ):

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

        entry = item.get(
            "entry"
        )

        tp = item.get(
            "tp"
        )

        sl = item.get(
            "sl"
        )

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if symbol != XAUUSD_SYMBOL_NORMALIZED:

            logger.info(
                f"REJECTED {symbol} | "
                f"ONLY {XAUUSD_SYMBOL_NORMALIZED}"
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
                f"CONFIDENCE={confidence} "
                f"< {MIN_CONFIDENCE}"
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
                    "INVALID BUY TP"
                )

                return False

            if sl >= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    "INVALID BUY SL"
                )

                return False

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        if signal == "SELL":

            if tp >= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    "INVALID SELL
