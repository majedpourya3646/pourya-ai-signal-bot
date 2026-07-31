# core/opportunity_engine.py

from core.logger import logger

from core.market_signal_bridge import (
    analyze_market_symbols
)

from config import (
    MIN_CONFIDENCE
)





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



        buy_score = float(

            item.get(

                "buy_score",

                0

            )

        )



        sell_score = float(

            item.get(

                "sell_score",

                0

            )

        )





        score += confidence * 0.6





        if buy_score > 0 or sell_score > 0:

            score += (

                max(

                    buy_score,

                    sell_score

                )

                *

                0.3

            )





        if item.get(

            "entry"

        ) and item.get(

            "tp"

        ) and item.get(

            "sl"

        ):

            score += 10





        return round(

            score,

            2

        )



    except Exception as e:


        logger.exception(e)


        return 0









def enrich_opportunity(
    item
):

    try:


        item["opportunity_score"] = calculate_opportunity_score(

            item

        )



        return item



    except Exception as e:


        logger.exception(e)


        return None










def find_best_opportunities():

    try:


        signals = analyze_market_symbols()



        if not signals:

            return []





        opportunities = []



        for item in signals:



            confidence = float(

                item.get(

                    "confidence",

                    0

                )

            )



            if confidence < MIN_CONFIDENCE:

                continue





            enriched = enrich_opportunity(

                item

            )



            if enriched:

                opportunities.append(

                    enriched

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

            f"BEST OPPORTUNITIES {len(opportunities)}"

        )



        return opportunities



    except Exception as e:


        logger.exception(e)


        return []









def get_top_opportunity():

    try:


        opportunities = find_best_opportunities()



        if opportunities:

            return opportunities[0]



        return None



    except Exception as e:


        logger.exception(e)


        return None
