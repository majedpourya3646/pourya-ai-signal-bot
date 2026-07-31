# core/market_signal_bridge.py

from core.logger import logger

from core.multi_timeframe import (
    analyze_symbol
)

from config import (
    SYMBOLS
)








def analyze_market_symbols():

    try:


        results = []





        for symbol in SYMBOLS:



            try:


                analysis = analyze_symbol(

                    symbol

                )



                if not analysis:


                    continue





                results.append(

                    analysis

                )





            except Exception as e:


                logger.exception(e)


                continue







        return results



    except Exception as e:


        logger.exception(e)


        return []









def analyze_single_symbol(
    symbol
):

    try:


        return analyze_symbol(

            symbol

        )



    except Exception as e:


        logger.exception(e)


        return None
