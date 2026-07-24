# core/market_intelligence.py

from core.ai_analyzer import (
    analyze_multiple_symbols
)

from core.market_discovery import (
    get_new_symbols
)

from core.pump_scanner_advanced import (
    scan_advanced_pumps
)

from core.logger import logger



def run_market_intelligence():

    try:


        symbols = get_new_symbols(
            50
        )



        analysis = analyze_multiple_symbols(
            symbols
        )



        pumps = scan_advanced_pumps(
            symbols
        )



        return {

            "symbols": symbols,

            "analysis": analysis,

            "pumps": pumps

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "symbols": [],

            "analysis": [],

            "pumps": []

        }




def get_best_signals(
    limit=10
):

    data = run_market_intelligence()



    signals = []



    for item in data.get(
        "analysis",
        []
    ):


        if item.get(
            "decision"
        ) != "WAIT":


            signals.append(
                item
            )



    return signals[:limit]
