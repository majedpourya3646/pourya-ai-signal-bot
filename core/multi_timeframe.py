# core/multi_timeframe.py

from core.logger import logger

from core.market import (
    get_multi_timeframe_data
)

from core.signal_engine import (
    analyze_signal
)

from config import (
    DEFAULT_TP,
    DEFAULT_SL
)





TIMEFRAME_WEIGHTS = {

    "15": 0.25,

    "60": 0.35,

    "240": 0.40

}








def analyze_symbol(
    symbol
):

    try:


        market_data = get_multi_timeframe_data(

            symbol

        )



        if not market_data:

            return None





        results = {}



        total_score = 0



        buy_score = 0

        sell_score = 0



        confidence = 0





        for timeframe, df in market_data.items():



            if df is None:

                continue



            signal = analyze_signal(

                df

            )



            if not signal:

                continue





            weight = TIMEFRAME_WEIGHTS.get(

                timeframe,

                0

            )



            results[timeframe] = signal





            score = (

                signal.get(

                    "confidence",

                    0

                )

                *

                weight

            )



            total_score += score





            if signal.get(

                "signal"

            ) == "BUY":


                buy_score += score



            elif signal.get(

                "signal"

            ) == "SELL":


                sell_score += score






        if not results:

            return None





        final_signal = "WAIT"





        if buy_score > sell_score:

            final_signal = "BUY"



        elif sell_score > buy_score:

            final_signal = "SELL"





        final_confidence = round(

            max(

                buy_score,

                sell_score

            ),

            2

        )





        last_data = results.get(

            "15"

        )



        if not last_data:

            last_data = list(

                results.values()

            )[0]





        entry = last_data.get(

            "entry"

        )



        if not entry:

            return None






        if final_signal == "BUY":


            tp = entry * (

                1 +

                DEFAULT_TP / 100

            )


            sl = entry * (

                1 -

                DEFAULT_SL / 100

            )



        elif final_signal == "SELL":


            tp = entry * (

                1 -

                DEFAULT_TP / 100

            )


            sl = entry * (

                1 +

                DEFAULT_SL / 100

            )



        else:


            tp = None

            sl = None






        return {


            "symbol":

                symbol,



            "signal":

                final_signal,



            "confidence":

                final_confidence,



            "entry":

                entry,



            "tp":

                tp,



            "sl":

                sl,



            "timeframes":

                results,



            "buy_score":

                round(

                    buy_score,

                    2

                ),



            "sell_score":

                round(

                    sell_score,

                    2

                )

        }




    except Exception as e:


        logger.exception(e)


        return None









def analyze_symbols(
    symbols
):

    try:


        results = []



        for symbol in symbols:


            analysis = analyze_symbol(

                symbol

            )



            if analysis:

                results.append(

                    analysis

                )



        results.sort(

            key=lambda x:

                x.get(

                    "confidence",

                    0

                ),

            reverse=True

        )



        return results



    except Exception as e:


        logger.exception(e)


        return []
