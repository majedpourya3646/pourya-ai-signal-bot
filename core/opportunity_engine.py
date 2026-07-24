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
            0
        )



        if confidence >= 80:

            score += 50


        elif confidence >= 65:

            score += 35



        signal = item.get(
            "signal",
            ""
        )



        if signal == "STRONG BUY":

            score += 30


        elif signal == "BUY":

            score += 20



        return score



    except Exception:


        return 0




def find_opportunities(limit=20):

    try:

        symbols = get_symbols(100)

        logger.info(f"TOTAL SYMBOLS: {len(symbols)}")

        signals = analyze_market_symbols(symbols)

        logger.info(f"SIGNALS FOUND: {len(signals)}")

        pumps = scan_advanced_pumps(symbols)

        logger.info(f"PUMPS FOUND: {len(pumps)}")

        opportunities = []

        for signal in signals:

            score = calculate_opportunity_score(signal)

            signal["opportunity_score"] = score

            opportunities.append(signal)

        for pump in pumps:

            opportunities.append({

                "symbol": pump.get("symbol"),

                "signal": "PUMP WATCH",

                "confidence": pump.get("score", 0),

                "entry": None,

                "tp": None,

                "sl": None,

                "opportunity_score": pump.get("score", 0)

            })

        logger.info(f"TOTAL OPPORTUNITIES: {len(opportunities)}")

        opportunities.sort(

            key=lambda x: x.get("opportunity_score", 0),

            reverse=True

        )

        return opportunities[:limit]

    except Exception as e:

        logger.exception(e)

        return []
    try:


        symbols = get_symbols(
            100
        )



        signals = analyze_market_symbols(
            symbols
        )



        pumps = scan_advanced_pumps(
            symbols
        )



        opportunities = []



        for signal in signals:


            score = calculate_opportunity_score(
                signal
            )



            signal["opportunity_score"] = score



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



        return opportunities[:limit]



    except Exception as e:


        logger.exception(
            e
        )


        return []
