# core/multi_timeframe.py

from core.market import (
    get_market_data
)

from core.signal_engine import (
    analyze_signal
)

from core.logger import logger

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)





TIMEFRAME_WEIGHTS = {

    "15":

        0.25,


    "60":

        0.35,


    "240":

        0.40

}









def calculate_target(
    price,
    side
):

    try:


        if side == "BUY":


            tp = price * (

                1

                +

                DEFAULT_TP / 100

            )



            sl = price * (

                1

                -

                DEFAULT_SL / 100

            )



        else:


            tp = price * (

                1

                -

                DEFAULT_TP / 100

            )



            sl = price * (

                1

                +

                DEFAULT_SL / 100

            )





        return round(tp, 6), round(sl, 6)



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



            if not candles:

                continue






            result = analyze_signal(

                candles

            )



            if not result:

                continue





            confidence = result.get(

                "confidence",

                0

            )



            weighted = confidence * weight



            total_score += weighted





            if result.get(

                "signal"

            ) == "BUY":


                buy_score += weighted



            elif result.get(

                "signal"

            ) == "SELL":


                sell_score += weighted





            last_price = result.get(

                "price"

            )





            timeframe_results[tf] = result








        if total_score < 50:

            return None







        if buy_score > sell_score:


            final_signal = "BUY"



            confidence = buy_score



        elif sell_score > buy_score:


            final_signal = "SELL"



            confidence = sell_score



        else:


            return None







        tp, sl = calculate_target(

            last_price,

            final_signal

        )







        return {


            "symbol":

                symbol,



            "signal":

                final_signal,



            "confidence":

                round(

                    confidence,

                    2

                ),



            "entry":

                last_price,



            "tp":

                tp,



            "sl":

                sl,



            "timeframes":

                timeframe_results

        }





    except Exception as e:


        logger.exception(e)


        return None
