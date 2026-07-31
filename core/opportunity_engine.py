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





        confidence = item.get(

            "confidence",

            0

        )



        if confidence >= 80:


            score += 40



        elif confidence >= 70:


            score += 30



        elif confidence >= MIN_CONFIDENCE:


            score += 20





        signal = item.get(

            "signal"

        )



        if signal in [

            "BUY",

            "SELL"

        ]:


            score += 20





        timeframes = item.get(

            "timeframes",

            {}

        )



        if len(timeframes) >= 3:


            score += 20





        entry = item.get(

            "entry"

        )



        tp = item.get(

            "tp"

        )



        sl = item.get(

            "sl"

        )



        if entry and tp and sl:


            risk = abs(

                entry - sl

            )


            reward = abs(

                tp - entry

            )



            if risk > 0:


                rr = reward / risk



                if rr >= 2:


                    score += 20





        return score



    except Exception as e:


        logger.exception(e)


        return 0










def scan_opportunities():

    try:


        markets = analyze_market_symbols()



        if not markets:


            return []







        opportunities = []





        for item in markets:



            confidence = item.get(

                "confidence",

                0

            )



            if confidence < MIN_CONFIDENCE:


                continue





            item["opportunity_score"] = calculate_opportunity_score(

                item

            )



            opportunities.append(

                item

            )








        opportunities.sort(

            key=lambda x:

            x.get(

                "opportunity_score",

                0

            ),

            reverse=True

        )





        return opportunities



    except Exception as e:


        logger.exception(e)


        return []









def get_best_opportunity():

    try:


        opportunities = scan_opportunities()



        if opportunities:


            return opportunities[0]



        return None



    except Exception as e:


        logger.exception(e)


        return None
