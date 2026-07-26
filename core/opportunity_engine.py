# core/opportunity_engine.py

from core.market_signal_bridge import (
    analyze_market_symbols
)

from core.coin_scanner import (
    get_symbols
)

from core.pump_scanner_advanced import (
    scan_advanced_pumps
)

from core.logger import logger



def calculate_opportunity_score(
    item
):

    try:

        score = 0


        confidence = item.get(
            "confidence",
            item.get("score", 0)
        )


        if confidence >= 80:

            score += 50


        elif confidence >= 65:

            score += 35


        elif confidence >= 50:

            score += 20



        signal = item.get(
            "signal",
            ""
        )


        if signal in [
            "STRONG BUY",
            "STRONG SELL"
        ]:

            score += 30


        elif signal in [
            "BUY",
            "SELL"
        ]:

            score += 20



        return score



    except Exception as e:

        logger.exception(e)

        return 0




def find_opportunities(
    limit=20
):

    try:

        symbols = get_symbols()


        logger.info(
            f"TOTAL SYMBOLS: {len(symbols)}"
        )


        if not symbols:

            return []



        signals = analyze_market_symbols(
            symbols
        )


        logger.info(
            f"SIGNALS FOUND: {len(signals)}"
        )



        pumps = scan_advanced_pumps(
            symbols
        )


        logger.info(
            f"PUMPS FOUND: {len(pumps)}"
        )



        opportunities = []



        for signal in signals:


            signal["opportunity_score"] = calculate_opportunity_score(
                signal
            )


            opportunities.append(
                signal
            )



        for pump in pumps:


            opportunities.append(

                {

                    "symbol": pump.get(
                        "symbol"
                    ),

                    "signal": "PUMP WATCH",

                    "confidence": pump.get(
                        "score",
                        0
                    ),

                    "entry": None,

                    "tp": None,

                    "sl": None,

                    "opportunity_score": pump.get(
                        "score",
                        0
                    )

                }

            )



        opportunities.sort(

            key=lambda x:

            x.get(
                "opportunity_score",
                0
            ),

            reverse=True

        )



        logger.info(
            f"TOTAL OPPORTUNITIES: {len(opportunities)}"
        )


        return opportunities[:limit]



    except Exception as e:

        logger.exception(e)

        return []
