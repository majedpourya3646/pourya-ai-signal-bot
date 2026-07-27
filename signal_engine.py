# signal_engine.py

import ta
import pandas as pd

from config import (
    MIN_CONFIDENCE
)

from market import get_market_data

from core.logger import logger



# =========================================
# SIGNAL ENGINE V3
# Multi Indicator AI Scoring System
# =========================================



def safe_value(value, default=0):

    try:

        if pd.isna(value):

            return default

        return float(value)

    except:

        return default





def calculate_indicators(df):

    try:

        close = df["close"]

        high = df["high"]

        low = df["low"]


        # EMA

        df["ema20"] = ta.trend.EMAIndicator(
            close,
            window=20
        ).ema_indicator()


        df["ema50"] = ta.trend.EMAIndicator(
            close,
            window=50
        ).ema_indicator()


        df["ema200"] = ta.trend.EMAIndicator(
            close,
            window=200
        ).ema_indicator()



        # RSI

        df["rsi"] = ta.momentum.RSIIndicator(
            close,
            window=14
        ).rsi()



        # MACD

        macd = ta.trend.MACD(
            close
        )


        df["macd"] = macd.macd()

        df["macd_signal"] = macd.macd_signal()

        df["macd_hist"] = macd.macd_diff()



        # ADX

        adx = ta.trend.ADXIndicator(
            high,
            low,
            close,
            window=14
        )


        df["adx"] = adx.adx()



        # Volume

        df["volume_avg"] = (
            df["volume"]
            .rolling(20)
            .mean()
        )



        # Momentum

        df["momentum"] = (
            close
            -
            close.shift(10)
        )



        return df



    except Exception as e:

        logger.exception(e)

        return df







def analyze_signal(df):

    try:


        if df.empty or len(df) < 200:

            return {

                "signal": "WAIT",

                "confidence": 0,

                "reasons": []

            }



        df = calculate_indicators(
            df
        )


        last = df.iloc[-1]

        previous = df.iloc[-2]



        buy_score = 0

        sell_score = 0


        buy_reasons = []

        sell_reasons = []



        # ==========================
        # EMA TREND
        # ==========================


        if last["ema20"] > last["ema50"]:


            buy_score += 15

            buy_reasons.append(
                "EMA20 above EMA50"
            )


        elif last["ema20"] < last["ema50"]:


            sell_score += 15

            sell_reasons.append(
                "EMA20 below EMA50"
            )





        if last["ema50"] > last["ema200"]:


            buy_score += 15

            buy_reasons.append(
                "Long trend bullish"
            )


        elif last["ema50"] < last["ema200"]:


            sell_score += 15

            sell_reasons.append(
                "Long trend bearish"
            )





        # ==========================
        # RSI
        # ==========================


        rsi = safe_value(
            last["rsi"]
        )



        if 50 <= rsi <= 68:


            buy_score += 15

            buy_reasons.append(
                "RSI bullish zone"
            )



        elif 32 <= rsi <= 50:


            sell_score += 15

            sell_reasons.append(
                "RSI bearish zone"
            )





        elif rsi > 75:


            sell_score += 10

            sell_reasons.append(
                "RSI overbought"
            )





        # ==========================
        # MACD
        # ==========================


        if (

            last["macd"]

            >

            last["macd_signal"]

            and

            previous["macd"]

            <=

            previous["macd_signal"]

        ):


            buy_score += 20

            buy_reasons.append(
                "MACD bullish crossover"
            )



        elif (

            last["macd"]

            <

            last["macd_signal"]

            and

            previous["macd"]

            >=

            previous["macd_signal"]

        ):


            sell_score += 20

            sell_reasons.append(
                "MACD bearish crossover"
            )
        # ==========================
        # ADX TREND POWER
        # ==========================


        adx = safe_value(
            last["adx"]
        )


        if adx >= 25:


            if buy_score >= sell_score:

                buy_score += 10

                buy_reasons.append(
                    "Strong trend strength"
                )


            else:

                sell_score += 10

                sell_reasons.append(
                    "Strong bearish trend"
                )





        # ==========================
        # VOLUME SPIKE
        # ==========================


        volume = safe_value(
            last["volume"]
        )


        avg_volume = safe_value(
            last["volume_avg"]
        )



        if avg_volume > 0:


            volume_ratio = (
                volume /
                avg_volume
            )



            if volume_ratio >= 1.5:


                if buy_score >= sell_score:


                    buy_score += 15

                    buy_reasons.append(
                        "Volume spike"
                    )


                else:


                    sell_score += 15

                    sell_reasons.append(
                        "Selling volume spike"
                    )





        # ==========================
        # MOMENTUM
        # ==========================


        momentum = safe_value(
            last["momentum"]
        )



        if momentum > 0:


            buy_score += 10

            buy_reasons.append(
                "Positive momentum"
            )


        elif momentum < 0:


            sell_score += 10

            sell_reasons.append(
                "Negative momentum"
            )





        # ==========================
        # BREAKOUT CHECK
        # ==========================


        recent_high = (
            df["high"]
            .rolling(20)
            .max()
            .iloc[-2]
        )


        recent_low = (
            df["low"]
            .rolling(20)
            .min()
            .iloc[-2]
        )



        current_price = safe_value(
            last["close"]
        )



        if current_price > recent_high:


            buy_score += 15

            buy_reasons.append(
                "20 candle breakout"
            )



        elif current_price < recent_low:


            sell_score += 15

            sell_reasons.append(
                "20 candle breakdown"
            )





        # ==========================
        # FINAL DECISION
        # ==========================


        confidence = max(
            buy_score,
            sell_score
        )



        signal = "WAIT"

        reasons = []



        if (

            buy_score >= MIN_CONFIDENCE

            and

            buy_score > sell_score

        ):


            signal = "BUY"

            reasons = buy_reasons



        elif (

            sell_score >= MIN_CONFIDENCE

            and

            sell_score > buy_score

        ):


            signal = "SELL"

            reasons = sell_reasons





        # ==========================
        # SIGNAL QUALITY
        # ==========================


        if signal == "BUY":


            if confidence >= 85:

                signal = "STRONG BUY"


            elif confidence >= 70:

                signal = "BUY"


            else:

                signal = "EARLY BUY"





        elif signal == "SELL":


            if confidence >= 85:

                signal = "STRONG SELL"


            elif confidence >= 70:

                signal = "SELL"


            else:

                signal = "EARLY SELL"





        logger.info(
            f"SIGNAL {signal} | CONF={confidence}"
        )



        return {

            "signal": signal,

            "confidence": round(
                confidence,
                2
            ),

            "reasons": reasons,

        }





    except Exception as e:


        logger.exception(
            e
        )


        return {

            "signal": "WAIT",

            "confidence": 0,

            "reasons": []

        }







def get_signal(symbol):

    try:


        df = get_market_data(
            symbol,
            interval="15"
        )


        return analyze_signal(
            df
        )



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "signal": "WAIT",

            "confidence": 0,

            "reasons": []

        }
