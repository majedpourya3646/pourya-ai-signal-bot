# core/signal_engine.py

import pandas as pd

from core.logger import logger

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)





try:

    import ta

except Exception:

    ta = None







def calculate_indicators(
    df
):

    try:


        if df is None or df.empty:

            return None



        data = df.copy()



        if ta:


            data["ema20"] = ta.trend.ema_indicator(

                data["close"],

                window=20

            )


            data["ema50"] = ta.trend.ema_indicator(

                data["close"],

                window=50

            )


            data["ema200"] = ta.trend.ema_indicator(

                data["close"],

                window=200

            )



            data["rsi"] = ta.momentum.rsi(

                data["close"],

                window=14

            )



            data["macd"] = ta.trend.macd(

                data["close"]

            )



            data["adx"] = ta.trend.adx(

                data["high"],

                data["low"],

                data["close"]

            )



        else:


            data["ema20"] = (

                data["close"]

                .ewm(span=20)

                .mean()

            )


            data["ema50"] = (

                data["close"]

                .ewm(span=50)

                .mean()

            )


            data["ema200"] = (

                data["close"]

                .ewm(span=200)

                .mean()

            )



            data["rsi"] = 50



            data["macd"] = 0



            data["adx"] = 0





        return data



    except Exception as e:


        logger.exception(e)


        return None







def analyze_signal(
    df
):

    try:


        data = calculate_indicators(

            df

        )



        if data is None:

            return None





        last = data.iloc[-1]



        score = 0



        signal = "WAIT"





        # Trend

        if last["ema20"] > last["ema50"]:

            score += 20


        if last["ema50"] > last["ema200"]:

            score += 20



        if last["ema20"] < last["ema50"]:

            score -= 20


        if last["ema50"] < last["ema200"]:

            score -= 20





        # RSI

        if last["rsi"] < 35:

            score += 15


        elif last["rsi"] > 65:

            score -= 15





        # MACD

        if last["macd"] > 0:

            score += 15

        else:

            score -= 15





        # ADX

        if last["adx"] > 20:

            score += 10





        # Volume

        if (

            last["volume"]

            >

            data["volume"]

            .mean()

        ):

            score += 10





        confidence = abs(score)





        if score >= 40:


            signal = "BUY"



        elif score <= -40:


            signal = "SELL"





        return {


            "signal":

                signal,


            "confidence":

                min(

                    confidence,

                    100

                ),



            "price":

                float(

                    last["close"]

                ),



            "entry":

                float(

                    last["close"]

                ),



            "tp":

                float(

                    last["close"]

                )

                *

                (

                    1 +

                    DEFAULT_TP / 100

                )

                if signal=="BUY"

                else

                float(

                    last["close"]

                )

                *

                (

                    1 -

                    DEFAULT_TP / 100

                ),



            "sl":

                float(

                    last["close"]

                )

                *

                (

                    1 -

                    DEFAULT_SL / 100

                )

                if signal=="BUY"

                else

                float(

                    last["close"]

                )

                *

                (

                    1 +

                    DEFAULT_SL / 100

                )

        }



    except Exception as e:


        logger.exception(e)


        return None







def get_signal_strength(
    result
):

    try:


        confidence = result.get(

            "confidence",

            0

        )



        if confidence >= 80:

            return "STRONG"



        if confidence >= 60:

            return "NORMAL"



        return "WEAK"



    except Exception:


        return "UNKNOWN"
