# core/market_signal_bridge.py

from core.logger import logger

from core.multi_timeframe import (
    analyze_symbol
)

from config import (
    SYMBOLS
)






def normalize_signal(
    signal
):

    try:


        signal = str(

            signal

        ).upper().strip()



        if signal in [

            "STRONG BUY",

            "EARLY BUY"

        ]:

            return "BUY"



        if signal in [

            "STRONG SELL",

            "EARLY SELL"

        ]:

            return "SELL"



        return signal



    except Exception:


        return "WAIT"










def analyze_market_symbol(
    symbol
):

    try:


        result = analyze_symbol(

            symbol

        )



        if not result:

            return None





        signal = normalize_signal(

            result.get(

                "signal",

                "WAIT"

            )

        )



        if signal not in [

            "BUY",

            "SELL"

        ]:

            return None





        return {


            "symbol":

                symbol,



            "signal":

                signal,



            "confidence":

                result.get(

                    "confidence",

                    0

                ),



            "entry":

                result.get(

                    "entry"

                ),



            "tp":

                result.get(

                    "tp"

                ),



            "sl":

                result.get(

                    "sl"

                ),



            "buy_score":

                result.get(

                    "buy_score",

                    0

                ),



            "sell_score":

                result.get(

                    "sell_score",

                    0

                ),



            "timeframes":

                result.get(

                    "timeframes",

                    {}

                )

        }



    except Exception as e:


        logger.exception(e)


        return None










def analyze_market_symbols(
    symbols=None
):

    try:


        if symbols is None:

            symbols = SYMBOLS





        opportunities = []



        for symbol in symbols:



            result = analyze_market_symbol(

                symbol

            )



            if result:

                opportunities.append(

                    result

                )





        opportunities.sort(

            key=lambda x:

            x.get(

                "confidence",

                0

            ),

            reverse=True

        )



        logger.info(

            f"MARKET SIGNALS FOUND {len(opportunities)}"

        )



        return opportunities



    except Exception as e:


        logger.exception(e)


        return []










def get_best_signal():

    try:


        signals = analyze_market_symbols()



        if not signals:

            return None



        return signals[0]



    except Exception as e:


        logger.exception(e)


        return None
