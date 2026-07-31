# core/signal_engine.py

import pandas as pd

from ta.momentum import RSIIndicator

from ta.trend import (
    EMAIndicator,
    MACD,
    ADXIndicator
)

from core.logger import logger





def prepare_dataframe(
    candles
):

    try:


        df = pd.DataFrame(

            candles

        )



        if df.empty:

            return None





        df["close"] = df["close"].astype(float)

        df["high"] = df["high"].astype(float)

        df["low"] = df["low"].astype(float)

        df["volume"] = df["volume"].astype(float)



        return df



    except Exception as e:


        logger.exception(e)


        return None







def calculate_indicators(
    df
):

    try:


        df["ema20"] = EMAIndicator(

            df["close"],

            window=20

        ).ema_indicator()



        df["ema50"] = EMAIndicator(

            df["close"],

            window=50

        ).ema_indicator()



        df["ema200"] = EMAIndicator(

            df["close"],

            window=200

        ).ema_indicator()





        rsi = RSIIndicator(

            df["close"],

            window=14

        )



        df["rsi"] = rsi.rsi()






        macd = MACD(

            df["close"]

        )



        df["macd"] = macd.macd()

        df["macd_signal"] = macd.macd_signal()





        adx = ADXIndicator(

            df["high"],

            df["low"],

            df["close"]

        )



        df["adx"] = adx.adx()





        return df



    except Exception as e:


        logger.exception(e)


        return None







def analyze_signal(
    candles
):

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



        score = 0

        signal = None






        # Trend

        if last["ema20"] > last["ema50"]:

            score += 15



        if last["close"] > last["ema200"]:

            score += 15






        # RSI

        if 40 < last["rsi"] < 70:

            score += 15





        elif last["rsi"] < 30:

            score += 10






        # MACD

        if last["macd"] > last["macd_signal"]:

            score += 15






        # ADX

        if last["adx"] > 20:

            score += 15






        # Volume

        avg_volume = df["volume"].mean()



        if last["volume"] > avg_volume:

            score += 10






        if score >= 60:


            if (

                last["ema20"]

                >

                last["ema50"]

            ):


                signal = "BUY"



            else:


                signal = "SELL"







        return {


            "signal":

                signal,



            "confidence":

                min(

                    score,

                    100

                ),



            "price":

                float(

                    last["close"]

                ),



            "rsi":

                float(

                    last["rsi"]

                ),



            "adx":

                float(

                    last["adx"]

                )

        }



    except Exception as e:


        logger.exception(e)


        return None
