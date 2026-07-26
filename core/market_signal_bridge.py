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


                if not result:

                    continue



                logger.info(
                    f"{symbol} RESULT: {result}"
                )



                results.append(

                    {

                        "symbol": symbol,

                        "signal": result.get(
                            "signal",
                            "WAIT"
                        ),

                        "confidence": result.get(
                            "score",
                            0
                        ),

                        "score": result.get(
                            "score",
                            0
                        ),

                        "entry": result.get(
                            "entry",
                            result.get("price")
                        ),

                        "tp": result.get(
                            "take_profit"
                        ),

                        "sl": result.get(
                            "stop_loss"
                        ),

                        "price": result.get(
                            "price"
                        ),

                        "timeframes": result.get(
                            "timeframes",
                            []
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



        logger.info(
            f"MARKET SIGNALS GENERATED: {len(results)}"
        )


        return results



    except Exception as e:

        logger.exception(
            e
        )

        return []
