# core/market_signal_bridge.py

from multi_timeframe import analyze_symbol

from core.signal_validator import (
    validate_signal
)

from core.logger import logger



def analyze_market_symbols(
    symbols
):

    results = []



    try:


        for symbol in symbols:


            try:


                analysis = analyze_symbol(
                    symbol
                )



                if not analysis:

                    continue



                if validate_signal(
                    analysis
                ):


                    results.append(

                        {

                            "symbol": symbol,

                            "signal": analysis.get(
                                "signal"
                            ),

                            "confidence": analysis.get(
                                "confidence"
                            ),

                            "entry": analysis.get(
                                "entry"
                            ),

                            "tp": analysis.get(
                                "tp"
                            ),

                            "sl": analysis.get(
                                "sl"
                            )

                        }

                    )



            except Exception as e:


                logger.exception(
                    e
                )



        results.sort(

            key=lambda x: x.get(
                "confidence",
                0
            ),

            reverse=True

        )



        return results



    except Exception as e:


        logger.exception(
            e
        )


        return []
