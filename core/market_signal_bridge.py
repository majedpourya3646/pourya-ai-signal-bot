# core/market_signal_bridge.py

from multi_timeframe import (
    analyze_symbol
)

from core.logger import logger



def analyze_market_symbols(
    symbols
):

    results = []



    try:


        for symbol in symbols:


            try:


                result = analyze_symbol(
                    symbol
                )

    logger.info(f"{symbol} RESULT: {result}")

                if not result:

                    continue



                results.append(

                    {

                        "symbol": symbol,

                        "signal": result.get(
                            "signal",
                            "WAIT"
                        ),

                        "confidence": result.get(
                            "confidence",
                            0
                        ),

                        "entry": result.get(
                            "entry"
                        ),

                        "tp": result.get(
                            "tp"
                        ),

                        "sl": result.get(
                            "sl"
                        ),

                        "grade": result.get(
                            "grade",
                            ""
                        )

                    }

                )



            except Exception as e:


                logger.error(

                    f"{symbol} ERROR {e}"

                )



        return results



    except Exception as e:


        logger.exception(
            e
        )


        return []
