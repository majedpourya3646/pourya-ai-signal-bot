# core/market_signal_bridge.py

from multi_timeframe import (
    analyze_symbol
)

from core.logger import logger

from datetime import datetime

from config import (
    MIN_CONFIDENCE
)




VALID_SIGNALS = [

    "BUY",

    "SELL",

    "STRONG BUY",

    "STRONG SELL",

    "EARLY BUY",

    "EARLY SELL",

]





def is_valid_signal(
    result
):

    try:


        if not result:


            return False




        signal = result.get(

            "signal",

            "WAIT"

        )



        score = float(

            result.get(

                "score",

                result.get(

                    "confidence",

                    0

                )

            )

        )





        if signal not in VALID_SIGNALS:


            return False





        if score < MIN_CONFIDENCE:


            return False





        return True




    except Exception as e:


        logger.exception(e)


        return False






def normalize_signal(
    signal
):

    try:


        if signal in VALID_SIGNALS:


            return signal



        return "WAIT"



    except Exception:


        return "WAIT"








def build_signal_item(
    symbol,
    result
):

    try:


        signal = normalize_signal(

            result.get(

                "signal",

                "WAIT"

            )

        )



        score = float(

            result.get(

                "score",

                result.get(

                    "confidence",

                    0

                )

            )

        )





        return {


            "symbol":

            symbol,



            "market":

            "FUTURES",



            "signal":

            signal,



            "confidence":

            score,



            "score":

            score,



            "entry":

            result.get(

                "entry",

                result.get(

                    "price"

                )

            ),



            "price":

            result.get(

                "price"

            ),



            "tp":

            result.get(

                "tp",

                result.get(

                    "take_profit"

                )

            ),



            "sl":

            result.get(

                "sl",

                result.get(

                    "stop_loss"

                )

            ),



            "take_profit":

            result.get(

                "take_profit"

            ),



            "stop_loss":

            result.get(

                "stop_loss"

            ),



            "timeframes":

            result.get(

                "timeframes",

                []

            ),



            "grade":

            result.get(

                "grade",

                ""

            ),



            "reasons":

            result.get(

                "reasons",

                []

            ),



            "created_at":

            datetime.utcnow().isoformat()

        }



    except Exception as e:


        logger.exception(e)


        return None







def analyze_market_symbols(
    symbols
):


    results = []



    try:



        if not symbols:


            return []





        for symbol in symbols:



            try:



                logger.info(

                    f"ANALYZING {symbol}"

                )





                result = analyze_symbol(

                    symbol

                )





                if not result:


                    continue






                logger.info(

                    f"{symbol} RESULT {result}"

                )





                if not is_valid_signal(

                    result

                ):



                    logger.info(

                        f"{symbol} FILTERED"

                    )


                    continue





                item = build_signal_item(

                    symbol,

                    result

                )





                if not item:


                    continue





                results.append(

                    item

                )





                logger.info(

                    f"{symbol} ACCEPTED | {item['signal']} | SCORE={item['score']}"

                )





            except Exception as e:



                logger.exception(e)





        results.sort(

            key=lambda x:

            x.get(

                "confidence",

                0

            ),

            reverse=True

        )





        logger.info(

            f"VALID MARKET SIGNALS: {len(results)}"

        )





        return results





    except Exception as e:


        logger.exception(e)


        return []
