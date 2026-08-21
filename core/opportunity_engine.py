from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)

from core.trade_manager import (
    get_open_trades
)


def calculate_opportunity_score(item):

    try:

        score = 0

        confidence = float(
            item.get(
                "confidence",
                0
            )
        )

        # ---------------------------
        # Confidence
        # ---------------------------

        if confidence >= 80:

            score += 40

        elif confidence >= 70:

            score += 30

        elif confidence >= MIN_CONFIDENCE:

            score += 20

        else:

            return 0

        # ---------------------------
        # Signal
        # ---------------------------

        signal = str(
            item.get(
                "signal",
                ""
            )
        ).upper()

        if signal in (
            "BUY",
            "SELL"
        ):

            score += 20

        else:

            return 0

        # ---------------------------
        # Multi timeframe
        # ---------------------------

        timeframes = item.get(
            "timeframes",
            {}
        )

        if len(timeframes) >= 3:

            score += 20

        # ---------------------------
        # Entry / TP / SL
        # ---------------------------

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

                if risk > 0:

                    rr = reward / risk

                    if rr >= 2:

                        score += 20

            except (
                TypeError,
                ValueError
            ):

                pass

        return score

    except Exception as e:

        logger.exception(
            f"OPPORTUNITY SCORE ERROR {e}"
        )

        return 0


def validate_opportunity(item):

    try:

        if not item:

            return False

        symbol = item.get(
            "symbol"
        )

        signal = str(
            item.get(
                "signal",
                ""
            )
        ).upper()

        confidence = float(
            item.get(
                "confidence",
                0
            )
        )

        entry = item.get(
            "entry"
        )

        tp = item.get(
            "tp"
        )

        sl = item.get(
            "sl"
        )

        if not symbol:

            return False

        if signal not in (
            "BUY",
            "SELL"
        ):

            return False

        if confidence < MIN_CONFIDENCE:

            logger.info(
                f"REJECTED {symbol} | "
                f"CONFIDENCE {confidence} < "
                f"{MIN_CONFIDENCE}"
            )

            return False

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

        entry = float(entry)
        tp = float(tp)
        sl = float(sl)

        # ---------------------------
        # BUY validation
        # ---------------------------

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

        # ---------------------------
        # SELL validation
        # ---------------------------

        if signal == "SELL":

            if tp >= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    "INVALID SELL TP"
                )

                return False

            if sl <= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    "INVALID SELL SL"
                )

                return False

        return True

    except Exception as e:

        logger.exception(
            f"OPPORTUNITY VALIDATION ERROR {e}"
        )

        return False


def scan_opportunities():

    try:

        # ---------------------------
        # Max open trades
        # ---------------------------

        open_trades = get_open_trades()

        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(
                "MAX OPEN TRADES REACHED"
            )

            return []

        # ---------------------------
        # Market analysis
        # ---------------------------

        markets = analyze_market_symbols()

        if not markets:

            logger.warning(
                "NO MARKET DATA"
            )

            return []

        opportunities = []

        # ---------------------------
        # Analyze markets
        # ---------------------------

        for item in markets:

            try:

                symbol = item.get(
                    "symbol",
                    "UNKNOWN"
                )

                confidence = item.get(
                    "confidence",
                    0
                )

                signal = item.get(
                    "signal",
                    "NONE"
                )

                logger.info(
                    f"ANALYSIS {symbol} | "
                    f"SIGNAL={signal} | "
                    f"CONFIDENCE={confidence}"
                )

                # -------------------
                # Validation
                # -------------------

                if not validate_opportunity(
                    item
                ):

                    continue

                # -------------------
                # Score
                # -------------------

                score = calculate_opportunity_score(
                    item
                )

                if score <= 0:

                    continue

                item[
                    "opportunity_score"
                ] = score

                logger.info(
                    f"OPPORTUNITY {symbol} "
                    f"SCORE={score}"
                )

                opportunities.append(
                    item
                )

            except Exception as e:

                logger.exception(
                    f"OPPORTUNITY ITEM ERROR {e}"
                )

        # ---------------------------
        # Sort
        # ---------------------------

        opportunities.sort(
            key=lambda x: x.get(
                "opportunity_score",
                0
            ),
            reverse=True
        )

        return opportunities

    except Exception as e:

        logger.exception(
            f"SCAN OPPORTUNITIES ERROR {e}"
        )

        return []


def get_best_opportunity():

    try:

        opportunities = scan_opportunities()

        if not opportunities:

            logger.info(
                "NO VALID OPPORTUNITY"
            )

            return None

        best = opportunities[0]

        logger.info(
            f"BEST OPPORTUNITY "
            f"{best.get('symbol')} "
            f"SCORE={best.get('opportunity_score')}"
        )

        return best

    except Exception as e:

        logger.exception(
            f"BEST OPPORTUNITY ERROR {e}"
        )

        return None


def find_best_opportunity():

    """
    Compatibility wrapper for trading_loop.py.
    """

    return get_best_opportunity()
