# core/opportunity_engine.py

from core.scanner_service import (
    get_top_opportunities
)

from multi_timeframe import analyze_symbol

from core.signal_validator import (
    validate_signal
)

from core.logger import logger



def find_opportunities(
    limit=10
):

    opportunities = []


    try:


        markets = get_top_opportunities(
            limit
        )


        for market in markets:


            symbol = market.get(
                "symbol"
            )


            if not symbol:

                continue



            analysis = analyze_symbol(
                symbol
            )



            if validate_signal(
                analysis
            ):


                opportunities.append(

                    {

                        "symbol": symbol,

                        "market_score": market.get(
                            "score",
                            0
                        ),

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



        opportunities.sort(

            key=lambda x: x.get(
                "confidence",
                0
            ),

            reverse=True

        )


        return opportunities



    except Exception as e:


        logger.exception(
            e
        )


        return []
