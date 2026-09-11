# core/multi_timeframe.py

from core.market import get_market_data
from core.signal_engine import analyze_signal
from core.logger import logger

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)


# ============================================================
# Timeframe Configuration
# ============================================================

TIMEFRAME_WEIGHTS = {
    "15": 0.25,
    "60": 0.35,
    "240": 0.40
}


# ============================================================
# Target Calculation
# ============================================================

def calculate_target(
    price,
    side
):

    try:

        if price is None:
            return None, None

        price = float(price)

        if price <= 0:
            return None, None

        side = str(
            side or ""
        ).upper().strip()

        if side == "BUY":

            tp = price * (
                1 + DEFAULT_TP / 100
            )

            sl = price * (
                1 - DEFAULT_SL / 100
            )

        elif side == "SELL":

            tp = price * (
                1 - DEFAULT_TP / 100
            )

            sl = price * (
                1 + DEFAULT_SL / 100
            )

        else:

            return None, None

        return (
            round(tp, 6),
            round(sl, 6)
        )

    except Exception as e:

        logger.exception(e)

        return None, None


# ============================================================
# Weight Normalization
# ============================================================

def normalize_weights(
    available_timeframes
):

    try:

        if not available_timeframes:
            return {}

        available = [
            str(tf)
            for tf in available_timeframes
            if str(tf) in TIMEFRAME_WEIGHTS
        ]

        if not available:
            return {}

        total_weight = sum(
            TIMEFRAME_WEIGHTS[tf]
            for tf in available
        )

        if total_weight <= 0:
            return {}

        return {
            tf: TIMEFRAME_WEIGHTS[tf] / total_weight
            for tf in available
        }

    except Exception as e:

        logger.exception(e)

        return {}


# ============================================================
# MTF Agreement
# ============================================================

def calculate_mtf_agreement(
    timeframe_results
):

    try:

        if not timeframe_results:
            return 0.0

        signals = []

        for result in timeframe_results.values():

            if not isinstance(result, dict):
                continue

            signal = str(
                result.get("signal") or ""
            ).upper().strip()

            if signal in (
                "BUY",
                "SELL"
            ):

                signals.append(
                    signal
                )

        if not signals:
            return 0.0

        buy_count = signals.count(
            "BUY"
        )

        sell_count = signals.count(
            "SELL"
        )

        dominant_count = max(
            buy_count,
            sell_count
        )

        return round(
            dominant_count / len(signals) * 100,
            2
        )

    except Exception as e:

        logger.exception(e)

        return 0.0


# ============================================================
# Analyze Symbol
# ============================================================

def analyze_symbol(
    symbol
):

    try:

        timeframe_results = {}

        last_price = None

        # ----------------------------------------------------
        # Collect available timeframe data first
        # ----------------------------------------------------

        for tf in TIMEFRAME_WEIGHTS:

            candles = get_market_data(
                symbol,
                tf
            )

            # ------------------------------------------------
            # Market data validation
            # ------------------------------------------------

            if candles is None:

                logger.warning(
                    f"NO MARKET DATA "
                    f"{symbol} TF={tf}"
                )

                continue

            try:

                candle_count = len(
                    candles
                )

            except Exception:

                logger.warning(
                    f"INVALID MARKET DATA "
                    f"{symbol} TF={tf}"
                )

                continue

            logger.info(
                f"MARKET DATA "
                f"{symbol} TF={tf} "
                f"COUNT={candle_count}"
            )

            if candle_count == 0:

                logger.warning(
                    f"NO CANDLES "
                    f"{symbol} TF={tf}"
                )

                continue

            # ------------------------------------------------
            # Signal analysis
            # ------------------------------------------------

            result = analyze_signal(
                candles
            )

            if not result:

                logger.warning(
                    f"NO SIGNAL RESULT "
                    f"{symbol} TF={tf}"
                )

                continue

            signal = str(
                result.get("signal") or ""
            ).upper().strip()

            confidence = result.get(
                "confidence",
                0
            )

            try:

                confidence = float(
                    confidence
                )

            except (
                TypeError,
                ValueError
            ):

                confidence = 0.0

            price = result.get(
                "price"
            )

            if price is not None:

                try:

                    price = float(
                        price
                    )

                    if price > 0:
                        last_price = price

                except (
                    TypeError,
                    ValueError
                ):

                    pass

            timeframe_results[
                str(tf)
            ] = result

            logger.info(
                f"SIGNAL "
                f"{symbol} "
                f"TF={tf} "
                f"{signal} "
                f"CONF={confidence}"
            )

        # ----------------------------------------------------
        # No timeframe data
        # ----------------------------------------------------

        if not timeframe_results:

            logger.warning(
                f"NO TIMEFRAME RESULT "
                f"{symbol}"
            )

            return None

        # ----------------------------------------------------
        # Normalize weights according to available data
        # ----------------------------------------------------

        normalized_weights = normalize_weights(
            timeframe_results.keys()
        )

        if not normalized_weights:

            logger.warning(
                f"NO VALID TIMEFRAME WEIGHTS "
                f"{symbol}"
            )

            return None

        # ----------------------------------------------------
        # Calculate weighted direction scores
        # ----------------------------------------------------

        buy_score = 0.0
        sell_score = 0.0

        weighted_total = 0.0

        for tf, result in timeframe_results.items():

            weight = normalized_weights.get(
                str(tf),
                0.0
            )

            confidence = result.get(
                "confidence",
                0
            )

            try:

                confidence = float(
                    confidence
                )

            except (
                TypeError,
                ValueError
            ):

                confidence = 0.0

            weighted_score = (
                confidence * weight
            )

            weighted_total += (
                weighted_score
            )

            signal = str(
                result.get("signal") or ""
            ).upper().strip()

            if signal == "BUY":

                buy_score += (
                    weighted_score
                )

            elif signal == "SELL":

                sell_score += (
                    weighted_score
                )

        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        if buy_score > sell_score:

            final_signal = "BUY"

            signal_strength = buy_score

        elif sell_score > buy_score:

            final_signal = "SELL"

            signal_strength = sell_score

        else:

            logger.info(
                f"NO DIRECTION "
                f"{symbol}"
            )

            return None

        # ----------------------------------------------------
        # Agreement
        # ----------------------------------------------------

        mtf_agreement = calculate_mtf_agreement(
            timeframe_results
        )

        # ----------------------------------------------------
        # Data coverage
        # ----------------------------------------------------

        expected_timeframes = len(
            TIMEFRAME_WEIGHTS
        )

        available_timeframes = len(
            timeframe_results
        )

        data_coverage = round(
            available_timeframes
            / expected_timeframes
            * 100,
            2
        )

        # ----------------------------------------------------
        # Price validation
        # ----------------------------------------------------

        if (
            last_price is None
            or last_price <= 0
        ):

            logger.warning(
                f"NO VALID PRICE "
                f"{symbol}"
            )

            return None

        # ----------------------------------------------------
        # Targets
        # ----------------------------------------------------

        tp, sl = calculate_target(
            last_price,
            final_signal
        )

        if tp is None or sl is None:

            logger.warning(
                f"INVALID TP SL "
                f"{symbol}"
            )

            return None

        # ----------------------------------------------------
        # Risk / Reward
        # ----------------------------------------------------

        if final_signal == "BUY":

            risk = last_price - sl
            reward = tp - last_price

        else:

            risk = sl - last_price
            reward = last_price - tp

        if risk <= 0:

            logger.warning(
                f"INVALID RISK "
                f"{symbol}"
            )

            return None

        risk_reward = round(
            reward / risk,
            3
        )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        result = {

            "symbol": symbol,

            "signal": final_signal,

            # Backward-compatible field.
            # This is a weighted signal strength,
            # NOT a probability.
            "confidence": round(
                signal_strength,
                2
            ),

            "signal_strength": round(
                signal_strength,
                2
            ),

            "weighted_total": round(
                weighted_total,
                2
            ),

            "mtf_agreement": mtf_agreement,

            "data_coverage": data_coverage,

            "entry": last_price,

            "price": last_price,

            "tp": tp,

            "sl": sl,

            "risk_reward": risk_reward,

            "timeframes": timeframe_results,

            "timeframe_weights": normalized_weights
        }

        logger.info(
            f"MTF SUMMARY "
            f"{symbol} "
            f"BUY={round(buy_score, 2)} "
            f"SELL={round(sell_score, 2)} "
            f"STRENGTH={round(signal_strength, 2)} "
            f"AGREEMENT={mtf_agreement}% "
            f"COVERAGE={data_coverage}% "
            f"RR={risk_reward}"
        )

        logger.info(
            f"FINAL ANALYSIS "
            f"{result}"
        )

        return result

    except Exception as e:

        logger.exception(e)

        return None


# multi_timeframe.py END
