# core/opportunity_engine.py

from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols
)

from core.trade_manager import (
    get_open_trades
)

from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)


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
        ).upper()

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

        if isinstance(
            timeframes,
            dict
        ) and len(timeframes) >= 3:

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

        # ----------------------------------------------------
        # Basic
        # ----------------------------------------------------

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
                f"CONFIDENCE={confidence} "
                f"< {MIN_CONFIDENCE}"
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
        # Positive Prices
        # ----------------------------------------------------

        if entry <= 0:

            return False

        if tp <= 0:

            return False

        if sl <= 0:

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

        elif signal == "SELL":

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

        open_trades = get_open_trades()

        if not open_trades:

            return False

        for trade in open_trades:

            if str(
                trade.get(
                    "symbol",
                    ""
                )
            ).upper() == str(
                symbol
            ).upper():

                return True

        return False

    except Exception as exc:

        logger.error(
            f"DUPLICATE TRADE CHECK ERROR {exc}"
        )

        return True


# ============================================================
# Scan Opportunities
# ============================================================

def scan_opportunities():

    try:

        # ----------------------------------------------------
        # Open Trades
        # ----------------------------------------------------

        open_trades = get_open_trades()

        if open_trades is None:

            open_trades = []

        if len(open_trades) >= MAX_OPEN_TRADES:

            logger.info(
                f"MAX OPEN TRADES REACHED "
                f"{len(open_trades)}/{MAX_OPEN_TRADES}"
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
        # Analyze Markets
        # ----------------------------------------------------

        for item in markets:

            try:

                symbol = item.get(
                    "symbol",
                    "UNKNOWN"
                )

                signal = str(
                    item.get(
                        "signal",
                        "NONE"
                    )
                ).upper()

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
            f"BEST OPPORTUNITY | "
            f"{best.get('symbol')} | "
            f"SIGNAL={best.get('signal')} | "
            f"CONFIDENCE={best.get('confidence')} | "
            f"SCORE={best.get('opportunity_score')} | "
            f"RR={best.get('risk_reward')}"
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
