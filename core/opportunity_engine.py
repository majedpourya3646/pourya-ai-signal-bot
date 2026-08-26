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


# ============================================================
# Calculate Opportunity Score
# ============================================================

def calculate_opportunity_score(item):

    try:

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

            return 0

        # ----------------------------------------------------
        # Signal
        # ----------------------------------------------------

        signal = str(
            item.get(
                "signal",
                ""
            )
        ).upper().strip()

        if signal not in (
            "BUY",
            "SELL"
        ):

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

                    elif rr >= 1.5:

                        score += 10

            except (
                TypeError,
                ValueError
            ):

                pass

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

            return False

        symbol = str(
            item.get(
                "symbol",
                ""
            )
        ).upper().strip()

        signal = str(
            item.get(
                "signal",
                ""
            )
        ).upper().strip()

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

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if symbol != XAUUSD_SYMBOL:

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
                    "INVALID SELL TP"
                )

                return False

            if sl <= entry:

                logger.info(
                    f"REJECTED {symbol} | "
                    "INVALID SELL SL"
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

            logger.info(
                f"REJECTED {symbol} | "
                "ZERO RISK"
            )

            return False

        rr = reward / risk

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

        symbol = str(
            symbol
        ).upper().strip()

        # ----------------------------------------------------
        # Database
        # ----------------------------------------------------

        open_trades = get_open_trades()

        if open_trades:

            for trade in open_trades:

                trade_symbol = str(
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
                    trade_symbol == symbol
                    and status in (
                        "OPEN",
                        "PAPER_OPEN",
                        "ACTIVE",
                    )
                ):

                    return True

        # ----------------------------------------------------
        # MT5
        # ----------------------------------------------------

        if has_open_position(
            symbol
        ):

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

        try:

            position_count = get_position_count()

            if position_count >= MAX_OPEN_TRADES:

                logger.info(
                    f"MAX MT5 POSITIONS REACHED "
                    f"{position_count}/"
                    f"{MAX_OPEN_TRADES}"
                )

                return []

        except Exception as exc:

            logger.error(
                f"POSITION COUNT ERROR {exc}"
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
                f"{len(open_trades)}/"
                f"{MAX_OPEN_TRADES}"
            )

            return []

        # ----------------------------------------------------
        # Market Analysis
        # ----------------------------------------------------

        markets = analyze_market_symbols()

        if not markets:

            logger.warning(
                "NO MARKET DATA"
            )

            return []

        opportunities = []

        # ----------------------------------------------------
        # Analyze only XAUUSD
        # ----------------------------------------------------

        for item in markets:

            try:

                symbol = str(
                    item.get(
                        "symbol",
                        ""
                    )
                ).upper().strip()

                if symbol != XAUUSD_SYMBOL:

                    continue

                signal = str(
                    item.get(
                        "signal",
                        "NONE"
                    )
                ).upper().strip()

                confidence = item.get(
                    "confidence",
                    0
                )

                logger.info(
                    f"ANALYSIS {symbol} | "
                    f"SIGNAL={signal} | "
                    f"CONFIDENCE={confidence}"
                )

                # ------------------------------------------------
                # Duplicate protection
                # ------------------------------------------------

                if has_open_trade(
                    symbol
                ):

                    logger.info(
                        f"SKIP {symbol} | "
                        "TRADE ALREADY OPEN"
                    )

                    continue

                # ------------------------------------------------
                # Validation
                # ------------------------------------------------

                if not validate_opportunity(
                    item
                ):

                    continue

                # ------------------------------------------------
                # Score
                # ------------------------------------------------

                score = calculate_opportunity_score(
                    item
                )

                if score <= 0:

                    continue

                item[
                    "opportunity_score"
                ] = score

                # ------------------------------------------------
                # Risk / Reward
                # ------------------------------------------------

                try:

                    entry = float(
                        item.get(
                            "entry"
                        )
                    )

                    tp = float(
                        item.get(
                            "tp"
                        )
                    )

                    sl = float(
                        item.get(
                            "sl"
                        )
                    )

                    risk = abs(
                        entry - sl
                    )

                    reward = abs(
                        tp - entry
                    )

                    item[
                        "risk_reward"
                    ] = (
                        reward / risk
                        if risk > 0
                        else 0
                    )

                except Exception:

                    item[
                        "risk_reward"
                    ] = 0

                logger.info(
                    f"OPPORTUNITY {symbol} | "
                    f"SIGNAL={signal} | "
                    f"CONFIDENCE={confidence} | "
                    f"SCORE={score} | "
                    f"RR={item.get('risk_reward')}"
                )

                opportunities.append(
                    item
                )

            except Exception as exc:

                logger.exception(
                    f"OPPORTUNITY ITEM ERROR {exc}"
                )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        opportunities.sort(
            key=lambda x: (
                x.get(
                    "opportunity_score",
                    0
                ),
                x.get(
                    "confidence",
                    0
                ),
                x.get(
                    "risk_reward",
                    0
                )
            ),
            reverse=True
        )

        return opportunities

    except Exception as exc:

        logger.exception(
            f"SCAN OPPORTUNITIES ERROR {exc}"
        )

        return []


# ============================================================
# Get Best Opportunity
# ============================================================

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
            "================================"
        )

        logger.info(
            "BEST OPPORTUNITY"
        )

        logger.info(
            f"SYMBOL={best.get('symbol')}"
        )

        logger.info(
            f"SIGNAL={best.get('signal')}"
        )

        logger.info(
            f"CONFIDENCE={best.get('confidence')}"
        )

        logger.info(
            f"SCORE={best.get('opportunity_score')}"
        )

        logger.info(
            f"RR={best.get('risk_reward')}"
        )

        logger.info(
            f"ENTRY={best.get('entry')}"
        )

        logger.info(
            f"SL={best.get('sl')}"
        )

        logger.info(
            f"TP={best.get('tp')}"
        )

        logger.info(
            "================================"
        )

        return best

    except Exception as exc:

        logger.exception(
            f"BEST OPPORTUNITY ERROR {exc}"
        )

        return None


# ============================================================
# Compatibility Wrapper
# ============================================================

def find_best_opportunity():

    return get_best_opportunity()
