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



        confidence = float(
            item.get(
                "confidence",
                0
            )
        )


        if confidence >= 90:

            score += 40

        elif confidence >= 80:

            score += 30

        elif confidence >= 70:

            score += 20



        volume = item.get(
            "volume_confirm",
            False
        )


        if volume:

            score += 15



        trend = item.get(
            "trend_confirm",
            False
        )


        if trend:

            score += 15



        breakout = item.get(
            "breakout",
            False
        )


        if breakout:

            score += 10



        return min(
            score,
            100
        )



    except Exception as e:


        logger.exception(e)


        return 0





def classify_opportunity(
    score
):

    try:


        if score >= 85:

            return "HIGH"



        elif score >= 70:

            return "MEDIUM"



        return "LOW"



    except:


        return "LOW"






def enrich_opportunity(
    item
):

    try:


        score = calculate_opportunity_score(
            item
        )


        item["opportunity_score"] = score


        item["risk_level"] = classify_opportunity(
            score
        )


        return item



    except Exception as e:


        logger.exception(e)


        return item






def get_market_opportunities():

    try:


        symbols = get_symbols()



        if not symbols:

            return []



        results = analyze_market_symbols(
            symbols
        )



        if not results:

            return []



        enriched = []



        for item in results:


            enriched.append(

                enrich_opportunity(
                    item
                )

            )



        return enriched



    except Exception as e:


        logger.exception(e)


        return []






def get_explosive_opportunities():

    try:


        pumps = scan_advanced_pumps()



        if not pumps:

            return []



        results = []



        for item in pumps:


            item = enrich_opportunity(
                item
            )


            if item.get(
                "opportunity_score",
                0
            ) >= 70:


                results.append(
                    item
                )



        return results



    except Exception as e:


        logger.exception(e)


        return []






def find_best_opportunities():

    try:


        opportunities = []



        market = get_market_opportunities()



        if market:

            opportunities.extend(
                market
            )



        explosive = get_explosive_opportunities()



        if explosive:

            opportunities.extend(
                explosive
            )



        if not opportunities:

            return []



        unique = {}



        for item in opportunities:


            symbol = item.get(
                "symbol"
            )


            if not symbol:

                continue



            old = unique.get(
                symbol
            )



            if not old:


                unique[symbol] = item



            else:


                if item.get(
                    "opportunity_score",
                    0
                ) > old.get(
                    "opportunity_score",
                    0
                ):

                    unique[symbol] = item



        final = list(
            unique.values()
        )



        final.sort(

            key=lambda x:

            x.get(
                "opportunity_score",
                0
            ),

            reverse=True

        )



        logger.info(

            f"BEST OPPORTUNITIES FOUND: {len(final)}"

        )


        return final



    except Exception as e:


        logger.exception(e)


        return []
