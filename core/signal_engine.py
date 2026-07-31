
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

            close=df["close"],

            window=20

        ).ema_indicator()



        df["ema50"] = EMAIndicator(

            close=df["close"],

            window=50

        ).ema_indicator()



        df["ema200"] = EMAIndicator(

            close=df["close"],

            window=200

        ).ema_indicator()






        rsi = RSIIndicator(

            close=df["close"],

            window=14

        )


        df["rsi"] = rsi.rsi()






        macd = MACD(

            close=df["close"]

        )


        df["macd"] = macd.macd()

        df["macd_signal"] = macd.macd_signal()






        adx = ADXIndicator(

            high=df["high"],

            low=df["low"],

            close=df["close"]

        )


        df["adx"] = adx.adx()





        df = df.dropna()



        if df.empty:

            return None



        return df



    except Exception as e:

        logger.exception(e)

        return None

def calculate_signal_score(
    last
):

    try:


        buy_score = 0

        sell_score = 0





        # EMA TREND

        if last["ema20"] > last["ema50"]:

            buy_score += 20


        elif last["ema20"] < last["ema50"]:

            sell_score += 20





        # EMA 200 FILTER

        if last["close"] > last["ema200"]:

            buy_score += 15


        elif last["close"] < last["ema200"]:

            sell_score += 15






        # RSI

        if last["rsi"] < 30:

            buy_score += 15


        elif last["rsi"] > 70:

            sell_score += 15


        elif 45 <= last["rsi"] <= 55:

            buy_score += 5

            sell_score += 5







        # MACD

        if last["macd"] > last["macd_signal"]:

            buy_score += 20


        elif last["macd"] < last["macd_signal"]:

            sell_score += 20






        # ADX TREND STRENGTH

        if last["adx"] > 20:

            if last["ema20"] > last["ema50"]:

                buy_score += 10

            else:

                sell_score += 10






        # VOLUME

        return {


            "buy_score":

                buy_score,


            "sell_score":

                sell_score

        }



    except Exception as e:


        logger.exception(e)


        return {


            "buy_score":

                0,


            "sell_score":

                0

        }









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





        logger.info(

            f"SIGNAL SCORE BUY={buy_score} SELL={sell_score}"

        )





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


            "rsi":

                round(

                    float(last["rsi"]),

                    2

                ),


            "adx":

                round(

                    float(last["adx"]),

                    2

                )

        }



    except Exception as e:


        logger.exception(e)


        return None

# signal_engine.py END


def get_signal_direction(
    candles
):

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
