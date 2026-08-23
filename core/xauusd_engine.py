# core/xauusd_engine.py

from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols
)

from config import (
    MIN_CONFIDENCE,
    MIN_RISK_REWARD
)


# ============================================================
# Configuration
# ============================================================

XAUUSD_SYMBOL = "XAUUSD"

REQUIRED_TIMEFRAMES = (
    "M15",
    "H1",
    "H4"
)


# ============================================================
# Helpers
# ============================================================

def _to_float(
    value,
    default=0.0
):

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


# ============================================================
# Validate XAUUSD
# ============================================================

def validate_xauusd(
    opportunity
):

    try:

        if not opportunity:

            return False

        symbol = str(
            opportunity.get(
                "symbol",
                ""
            )
        ).upper()

        if symbol != XAUUSD_SYMBOL:

            logger.info(
                f"XAUUSD ENGINE REJECTED "
                f"SYMBOL={symbol}"
            )

            return False

        signal = str(
            opportunity.get(
                "signal",
                ""
            )
        ).upper()

        if signal not in (
            "BUY",
            "SELL"
        ):

            logger.info(
                "XAUUSD ENGINE REJECTED "
                "INVALID SIGNAL"
            )

            return False

        confidence = _to_float(
            opportunity.get(
                "confidence"
            )
        )

        if confidence < MIN_CONFIDENCE:

            logger.info(
                f"XAUUSD REJECTED "
                f"CONFIDENCE={confidence}"
            )

            return False

        entry = _to_float(
            opportunity.get(
                "entry"
            )
        )

        tp = _to_float(
            opportunity.get(
                "tp"
            )
        )

        sl = _to_float(
            opportunity.get(
                "sl"
            )
        )

        if (
            entry <= 0
            or tp <= 0
            or sl <= 0
        ):

            logger.info(
                "XAUUSD REJECTED "
                "INVALID ENTRY/TP/SL"
            )

            return False

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if signal == "BUY":

            if not (
                sl < entry < tp
            ):

                logger.info(
                    "XAUUSD BUY "
                    "INVALID PRICE STRUCTURE"
                )

                return False

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        elif signal == "SELL":

            if not (
                tp < entry < sl
            ):

                logger.info(
                    "XAUUSD SELL "
                    "INVALID PRICE STRUCTURE"
                )

                return False

        # ----------------------------------------------------
        # Risk / Reward
        # ----------------------------------------------------

        risk = abs(
            entry - sl
        )

        reward = abs(
            tp - entry
        )

        if risk <= 0:

            return False

        rr = reward / risk

        if rr < MIN_RISK_REWARD:

            logger.info(
                f"XAUUSD REJECTED "
                f"RR={rr:.2f}"
            )

            return False

        opportunity[
            "risk_reward"
        ] = rr

        return True

    except Exception as exc:

        logger.exception(
            f"XAUUSD VALIDATION ERROR {exc}"
        )

        return False


# ============================================================
# Multi Timeframe Validation
# ============================================================

def validate_timeframes(
    opportunity
):

    try:

        timeframes = opportunity.get(
            "timeframes",
            {}
        )

        if not isinstance(
            timeframes,
            dict
        ):

            logger.warning(
                "XAUUSD INVALID TIMEFRAME DATA"
            )

            return False

        available = {
            str(key).upper()
            for key in timeframes.keys()
        }

        missing = [

            timeframe

            for timeframe
            in REQUIRED_TIMEFRAMES

            if timeframe not in available

        ]

        if missing:

            logger.info(
                f"XAUUSD MISSING TIMEFRAMES "
                f"{missing}"
            )

            return False

        return True

    except Exception as exc:

        logger.exception(
            f"XAUUSD TIMEFRAME ERROR {exc}"
        )

        return False


# ============================================================
# Calculate XAUUSD Score
# ============================================================

def calculate_xauusd_score(
    opportunity
):

    try:

        score = 0

        confidence = _to_float(
            opportunity.get(
                "confidence"
            )
        )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        if confidence >= 85:

            score += 40

        elif confidence >= 75:

            score += 30

        elif confidence >= MIN_CONFIDENCE:

            score += 20

        else:

            return 0

        # ----------------------------------------------------
        # Signal
        # ----------------------------------------------------

        signal = str(
            opportunity.get(
                "signal",
                ""
            )
        ).upper()

        if signal not in (
            "BUY",
            "SELL"
        ):

            return 0

        score += 20

        # ----------------------------------------------------
        # Timeframes
        # ----------------------------------------------------

        if validate_timeframes(
            opportunity
        ):

            score += 20

        # ----------------------------------------------------
        # Risk / Reward
        # ----------------------------------------------------

        rr = _to_float(
            opportunity.get(
                "risk_reward"
            )
        )

        if rr >= 3:

            score += 20

        elif rr >= 2:

            score += 15

        elif rr >= MIN_RISK_REWARD:

            score += 10

        return score

    except Exception as exc:

        logger.exception(
            f"XAUUSD SCORE ERROR {exc}"
        )

        return 0


# ============================================================
# Analyze XAUUSD
# ============================================================

def analyze_xauusd():

    try:

        logger.info(
            "================================"
        )

        logger.info(
            "XAUUSD ENGINE START"
        )

        logger.info(
            "================================"
        )

        markets = analyze_market_symbols()

        if not markets:

            logger.warning(
                "XAUUSD NO MARKET DATA"
            )

            return None

        xauusd = None

        for item in markets:

            symbol = str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper()

            if symbol == XAUUSD_SYMBOL:

                xauusd = item

                break

        if xauusd is None:

            logger.info(
                "XAUUSD NOT FOUND"
            )

            return None

        logger.info(
            f"XAUUSD SIGNAL="
            f"{xauusd.get('signal')} "
            f"CONFIDENCE="
            f"{xauusd.get('confidence')}"
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not validate_xauusd(
            xauusd
        ):

            logger.info(
                "XAUUSD VALIDATION FAILED"
            )

            return None

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score = calculate_xauusd_score(
            xauusd
        )

        if score <= 0:

            logger.info(
                "XAUUSD SCORE TOO LOW"
            )

            return None

        xauusd[
            "opportunity_score"
        ] = score

        logger.info(
            f"XAUUSD OPPORTUNITY "
            f"SCORE={score} "
            f"RR={xauusd.get('risk_reward')}"
        )

        return xauusd

    except Exception as exc:

        logger.exception(
            f"XAUUSD ENGINE ERROR {exc}"
        )

        return None


# ============================================================
# Best XAUUSD Opportunity
# ============================================================

def get_xauusd_opportunity():

    try:

        opportunity = analyze_xauusd()

        if not opportunity:

            logger.info(
                "NO XAUUSD OPPORTUNITY"
            )

            return None

        logger.info(
            f"BEST XAUUSD OPPORTUNITY "
            f"SIGNAL={opportunity.get('signal')} "
            f"ENTRY={opportunity.get('entry')} "
            f"TP={opportunity.get('tp')} "
            f"SL={opportunity.get('sl')} "
            f"CONFIDENCE={opportunity.get('confidence')} "
            f"SCORE={opportunity.get('opportunity_score')}"
        )

        return opportunity

    except Exception as exc:

        logger.exception(
            f"GET XAUUSD OPPORTUNITY ERROR {exc}"
        )

        return None
