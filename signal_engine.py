# signal_engine.py

import ta


from config import (
    MIN_CONFIDENCE
)

from market import get_market_data

from core.logger import logger



def analyze_signal(
    df
):

    try:

        if df.empty or len(df) < 200:

            return {

                "signal": "WAIT",

                "confidence": 0

            }



        close = df["close"]


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



        df["rsi"] = ta.momentum.RSIIndicator(
            close,
            window=14
        ).rsi()



        macd = ta.trend.MACD(
            close
        )


        df["macd"] = macd.macd()

        df["macd_signal"] = macd.macd_signal()



        adx = ta.trend.ADXIndicator(

            df["high"],

            df["low"],

            close

        )


        df["adx"] = adx.adx()



        score = 0

        reasons = []



        last = df.iloc[-1]



        if last["ema20"] > last["ema50"]:

            score += 15

            reasons.append(
                "EMA20 بالاتر از EMA50"
            )


        if last["ema50"] > last["ema200"]:

            score += 15

            reasons.append(
                "روند بلندمدت صعودی"
            )


        if 50 < last["rsi"] < 70:

            score += 15

            reasons.append(
                "RSI مناسب"
            )


        if last["macd"] > last["macd_signal"]:

            score += 15

            reasons.append(
                "MACD صعودی"
            )


        if last["adx"] > 25:

            score += 15

            reasons.append(
                "قدرت روند مناسب"
            )


        avg_volume = (
            df["volume"]
            .rolling(20)
            .mean()
            .iloc[-1]
        )


        if last["volume"] > avg_volume:

            score += 15

            reasons.append(
                "حجم افزایش یافته"
            )



        if score >= MIN_CONFIDENCE:


            return {

                "signal": "BUY",

                "confidence": score,

                "reasons": reasons

            }



        return {

            "signal": "WAIT",

            "confidence": score,

            "reasons": reasons

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

            "confidence": 0

        }
