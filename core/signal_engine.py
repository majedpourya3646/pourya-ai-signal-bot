# core/signal_engine.py

import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import (
    EMAIndicator,
    MACD,
    ADXIndicator
)

from core.logger import logger


# ============================================================
# Constants
# ============================================================

EMA_FAST_PERIOD = 20
EMA_SLOW_PERIOD = 50
EMA_TREND_PERIOD = 200

RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ADX_PERIOD = 14

# Score weights
EMA_TREND_SCORE = 20
EMA200_SCORE = 15
RSI_SCORE = 10
MACD_SCORE = 20
ADX_SCORE = 10
VOLUME_SCORE = 10

MAX_SIGNAL_SCORE = (
    EMA_TREND_SCORE
    + EMA200_SCORE
    + RSI_SCORE
    + MACD_SCORE
    + ADX_SCORE
    + VOLUME_SCORE
)


# ============================================================
# Data Preparation
# ============================================================

def prepare_dataframe(candles):
    try:

        df = pd.DataFrame(candles)

        if df.empty:
            return None

        required_columns = [
            "close",
            "high",
            "low",
            "volume"
        ]

        for column in required_columns:

            if column not in df.columns:

                logger.warning(
                    f"MISSING COLUMN {column}"
                )

                return None

        for column in required_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df = df.dropna(
            subset=required_columns
        )

        if df.empty:
            return None

        return df

    except Exception as e:

        logger.exception(e)

        return None


# ============================================================
# Indicators
# ============================================================

def calculate_indicators(df):

    try:

        if df is None or df.empty:
            return None

        df = df.copy()

        df["ema20"] = EMAIndicator(
            close=df["close"],
            window=EMA_FAST_PERIOD
        ).ema_indicator()

        df["ema50"] = EMAIndicator(
            close=df["close"],
            window=EMA_SLOW_PERIOD
        ).ema_indicator()

        df["ema200"] = EMAIndicator(
            close=df["close"],
            window=EMA_TREND_PERIOD
        ).ema_indicator()

        rsi = RSIIndicator(
            close=df["close"],
            window=RSI_PERIOD
        )

        df["rsi"] = rsi.rsi()

        macd = MACD(
            close=df["close"],
            window_fast=MACD_FAST,
            window_slow=MACD_SLOW,
            window_sign=MACD_SIGNAL
        )

        df["macd"] = macd.macd()

        df["macd_signal"] = macd.macd_signal()

        df["macd_histogram"] = macd.macd_diff()

        adx = ADXIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=ADX_PERIOD
        )

        df["adx"] = adx.adx()

        # Volume moving average
        df["volume_ma20"] = (
            df["volume"]
            .rolling(window=20)
            .mean()
        )

        df = df.dropna()

        if df.empty:
            return None

        return df

    except Exception as e:

        logger.exception(e)

        return None


# ============================================================
# Volume Analysis
# ============================================================

def calculate_volume_condition(last):

    try:

        volume = float(
            last["volume"]
        )

        volume_ma = float(
            last["volume_ma20"]
        )

        if volume_ma <= 0:
            return "NEUTRAL"

        ratio = volume / volume_ma

        if ratio >= 1.20:
            return "STRONG"

        if ratio >= 0.90:
            return "NORMAL"

        return "WEAK"

    except Exception:

        return "NEUTRAL"


# ============================================================
# Signal Score
# ============================================================

def calculate_signal_score(last):

    try:

        buy_score = 0
        sell_score = 0

        reasons_buy = []
        reasons_sell = []

        # ----------------------------------------------------
        # EMA 20 / 50 TREND
        # ----------------------------------------------------

        ema20 = float(last["ema20"])
        ema50 = float(last["ema50"])

        if ema20 > ema50:

            buy_score += EMA_TREND_SCORE

            reasons_buy.append(
                "EMA20_ABOVE_EMA50"
            )

        elif ema20 < ema50:

            sell_score += EMA_TREND_SCORE

            reasons_sell.append(
                "EMA20_BELOW_EMA50"
            )

        # ----------------------------------------------------
        # EMA 200 TREND FILTER
        # ----------------------------------------------------

        close = float(last["close"])
        ema200 = float(last["ema200"])

        if close > ema200:

            buy_score += EMA200_SCORE

            reasons_buy.append(
                "PRICE_ABOVE_EMA200"
            )

        elif close < ema200:

            sell_score += EMA200_SCORE

            reasons_sell.append(
                "PRICE_BELOW_EMA200"
            )

        # ----------------------------------------------------
        # RSI
        #
        # Trend-aware logic:
        #
        # RSI < 30 is NOT automatically BUY.
        # RSI > 70 is NOT automatically SELL.
        #
        # Extreme RSI is treated as exhaustion information.
        # ----------------------------------------------------

        rsi = float(last["rsi"])

        if 50 < rsi < 70:

            buy_score += RSI_SCORE

            reasons_buy.append(
                "RSI_BULLISH_ZONE"
            )

        elif 30 < rsi < 50:

            sell_score += RSI_SCORE

            reasons_sell.append(
                "RSI_BEARISH_ZONE"
            )

        elif 45 <= rsi <= 55:

            buy_score += RSI_SCORE // 2
            sell_score += RSI_SCORE // 2

        elif rsi <= 30:

            # Oversold does not automatically create BUY.
            # It is neutral unless other trend factors confirm.
            reasons_sell.append(
                "RSI_OVERSOLD_CAUTION"
            )

        elif rsi >= 70:

            # Overbought does not automatically create SELL.
            # It is neutral unless other trend factors confirm.
            reasons_buy.append(
                "RSI_OVERBOUGHT_CAUTION"
            )

        # ----------------------------------------------------
        # MACD
        # ----------------------------------------------------

        macd = float(
            last["macd"]
        )

        macd_signal = float(
            last["macd_signal"]
        )

        macd_histogram = float(
            last["macd_histogram"]
        )

        if macd > macd_signal and macd_histogram > 0:

            buy_score += MACD_SCORE

            reasons_buy.append(
                "MACD_BULLISH"
            )

        elif macd < macd_signal and macd_histogram < 0:

            sell_score += MACD_SCORE

            reasons_sell.append(
                "MACD_BEARISH"
            )

        # ----------------------------------------------------
        # ADX TREND STRENGTH
        #
        # ADX itself has no direction.
        # Direction comes from EMA20/EMA50.
        # ----------------------------------------------------

        adx = float(
            last["adx"]
        )

        if adx >= 25:

            if ema20 > ema50:

                buy_score += ADX_SCORE

                reasons_buy.append(
                    "ADX_STRONG_BULLISH_TREND"
                )

            elif ema20 < ema50:

                sell_score += ADX_SCORE

                reasons_sell.append(
                    "ADX_STRONG_BEARISH_TREND"
                )

        elif adx >= 20:

            # Moderate trend gets partial confirmation.
            partial_adx_score = ADX_SCORE // 2

            if ema20 > ema50:

                buy_score += partial_adx_score

                reasons_buy.append(
                    "ADX_MODERATE_BULLISH_TREND"
                )

            elif ema20 < ema50:

                sell_score += partial_adx_score

                reasons_sell.append(
                    "ADX_MODERATE_BEARISH_TREND"
                )

        # ----------------------------------------------------
        # VOLUME
        #
        # Volume confirms market participation.
        # It does not determine direction by itself.
        # ----------------------------------------------------

        volume_condition = calculate_volume_condition(
            last
        )

        if volume_condition == "STRONG":

            if ema20 > ema50:

                buy_score += VOLUME_SCORE

                reasons_buy.append(
                    "STRONG_VOLUME_BULLISH"
                )

            elif ema20 < ema50:

                sell_score += VOLUME_SCORE

                reasons_sell.append(
                    "STRONG_VOLUME_BEARISH"
                )

        elif volume_condition == "NORMAL":

            partial_volume_score = VOLUME_SCORE // 2

            if ema20 > ema50:

                buy_score += partial_volume_score

                reasons_buy.append(
                    "NORMAL_VOLUME_BULLISH"
                )

            elif ema20 < ema50:

                sell_score += partial_volume_score

                reasons_sell.append(
                    "NORMAL_VOLUME_BEARISH"
                )

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return {
            "buy_score": min(
                buy_score,
                MAX_SIGNAL_SCORE
            ),

            "sell_score": min(
                sell_score,
                MAX_SIGNAL_SCORE
            ),

            "reasons_buy": reasons_buy,

            "reasons_sell": reasons_sell,

            "volume_condition": volume_condition
        }

    except Exception as e:

        logger.exception(e)

        return {
            "buy_score": 0,
            "sell_score": 0,
            "reasons_buy": [],
            "reasons_sell": [],
            "volume_condition": "NEUTRAL"
        }


# ============================================================
# Signal Analysis
# ============================================================

def analyze_signal(candles):

    try:

        df = prepare_dataframe(
            candles
        )

        if df is None:
            return None

        df = calculate_indicators(
            df
        )

        if df is None:
            return None

        last = df.iloc[-1]

        scores = calculate_signal_score(
            last
        )

        buy_score = scores.get(
            "buy_score",
            0
        )

        sell_score = scores.get(
            "sell_score",
            0
        )

        signal = None

        confidence = max(
            buy_score,
            sell_score
        )

        if buy_score > sell_score:

            signal = "BUY"

        elif sell_score > buy_score:

            signal = "SELL"

        # ----------------------------------------------------
        # Detailed logging
        # ----------------------------------------------------

        logger.info(
            f"SIGNAL SCORE "
            f"BUY={buy_score} "
            f"SELL={sell_score}"
        )

        logger.info(
            f"SIGNAL DETAILS "
            f"RSI={round(float(last['rsi']), 2)} "
            f"ADX={round(float(last['adx']), 2)} "
            f"MACD={round(float(last['macd']), 6)} "
            f"MACD_SIGNAL={round(float(last['macd_signal']), 6)} "
            f"MACD_HIST={round(float(last['macd_histogram']), 6)} "
            f"VOLUME={scores.get('volume_condition')}"
        )

        if scores.get("reasons_buy"):

            logger.info(
                f"BUY REASONS "
                f"{scores.get('reasons_buy')}"
            )

        if scores.get("reasons_sell"):

            logger.info(
                f"SELL REASONS "
                f"{scores.get('reasons_sell')}"
            )

        return {

            "signal": signal,

            "confidence": min(
                confidence,
                100
            ),

            "price": float(
                last["close"]
            ),

            "rsi": round(
                float(last["rsi"]),
                2
            ),

            "adx": round(
                float(last["adx"]),
                2
            ),

            "macd": round(
                float(last["macd"]),
                8
            ),

            "macd_signal": round(
                float(last["macd_signal"]),
                8
            ),

            "macd_histogram": round(
                float(last["macd_histogram"]),
                8
            ),

            "volume_condition": scores.get(
                "volume_condition"
            ),

            "buy_score": buy_score,

            "sell_score": sell_score,

            "reasons_buy": scores.get(
                "reasons_buy",
                []
            ),

            "reasons_sell": scores.get(
                "reasons_sell",
                []
            )
        }

    except Exception as e:

        logger.exception(e)

        return None


# ============================================================
# Direction Helper
# ============================================================

def get_signal_direction(candles):

    try:

        result = analyze_signal(
            candles
        )

        if not result:
            return None

        return result.get(
            "signal"
        )

    except Exception as e:

        logger.exception(e)

        return None


# signal_engine.py END
