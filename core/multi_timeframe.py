# core/multi_timeframe.py

from core.market import get_market_data
from core.signal_engine import analyze_signal
from core.logger import logger

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)


TIMEFRAME_WEIGHTS = {
    "15": 0.25,
    "60": 0.35,
    "240": 0.40
}


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


def analyze_symbol(
    symbol
):
    try:
        total_score = 0
        buy_score = 0
        sell_score = 0
        last_price = None

        timeframe_results = {}

        for tf, weight in TIMEFRAME_WEIGHTS.items():

            candles = get_market_data(
                symbol,
                tf
            )

            # -------------------------------------------------
            # MARKET DATA VALIDATION
            # -------------------------------------------------

            if candles is None:
                logger.warning(
                    f"NO MARKET DATA {symbol} TF={tf}"
                )
                continue

            try:
                candle_count = len(candles)
            except Exception:
                logger.warning(
                    f"INVALID MARKET DATA {symbol} TF={tf}"
                )
                continue

            logger.info(
                f"MARKET DATA {symbol} TF={tf} COUNT={candle_count}"
            )

            if candle_count == 0:
                logger.warning(
                    f"NO CANDLES {symbol} TF={tf}"
                )
                continue

            # -------------------------------------------------
            # SIGNAL ANALYSIS
            # -------------------------------------------------

            result = analyze_signal(
                candles
            )

            if not result:
                logger.warning(
                    f"NO SIGNAL RESULT {symbol} TF={tf}"
                )
                continue

            confidence = result.get(
                "confidence",
                0
            )

            try:
                confidence = float(confidence)
            except (
                TypeError,
                ValueError
            ):
                confidence = 0

            weighted = confidence * weight

            total_score += weighted

            signal = result.get(
                "signal"
            )

            if signal == "BUY":
                buy_score += weighted

            elif signal == "SELL":
                sell_score += weighted

            price = result.get(
                "price"
            )

            if price is not None:
                try:
                    last_price = float(price)
                except (
                    TypeError,
                    ValueError
                ):
                    pass

            timeframe_results[tf] = result

            logger.info(
                f"SIGNAL {symbol} TF={tf} "
                f"{signal} CONF={confidence}"
            )

        # -----------------------------------------------------
        # NO TIMEFRAME DATA
        # -----------------------------------------------------

        if not timeframe_results:
            logger.warning(
                f"NO TIMEFRAME RESULT {symbol}"
            )
            return None

        # -----------------------------------------------------
        # SCORE VALIDATION
        # -----------------------------------------------------

        if total_score < 50:
            logger.info(
                f"LOW SCORE {symbol} SCORE={total_score}"
            )
            return None

        # -----------------------------------------------------
        # FINAL DIRECTION
        # -----------------------------------------------------

        if buy_score > sell_score:
            final_signal = "BUY"
            confidence = buy_score

        elif sell_score > buy_score:
            final_signal = "SELL"
            confidence = sell_score

        else:
            logger.info(
                f"NO DIRECTION {symbol}"
            )
            return None

        # -----------------------------------------------------
        # PRICE VALIDATION
        # -----------------------------------------------------

        if last_price is None or last_price <= 0:
            logger.warning(
                f"NO VALID PRICE {symbol}"
            )
            return None

        # -----------------------------------------------------
        # TARGETS
        # -----------------------------------------------------

        tp, sl = calculate_target(
            last_price,
            final_signal
        )

        if tp is None or sl is None:
            logger.warning(
                f"INVALID TP SL {symbol}"
            )
            return None

        # -----------------------------------------------------
        # FINAL RESULT
        # -----------------------------------------------------

        result = {
            "symbol": symbol,

            "signal": final_signal,

            "confidence": round(
                confidence,
                2
            ),

            "entry": last_price,

            "price": last_price,

            "tp": tp,

            "sl": sl,

            "timeframes": timeframe_results
        }

        logger.info(
            f"FINAL ANALYSIS {result}"
        )

        return result

    except Exception as e:
        logger.exception(e)
        return None
