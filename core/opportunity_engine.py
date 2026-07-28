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



        if confidence >= 85:

            score += 40


        elif confidence >= 70:

            score += 30


        elif confidence >= MIN_CONFIDENCE:

            score += 20




        signal = item.get(

            "signal",

            ""

        )



        if signal in [

            "STRONG BUY",

            "STRONG SELL"

        ]:

            score += 20



        elif signal in [

            "BUY",

            "SELL"

        ]:

            score += 10




        volume = item.get(

            "volume_score",

            0

        )



        try:

            score += min(

                float(volume),

                15

            )

        except:

            pass





        trend = item.get(

            "trend_score",

            0

        )



        try:

            score += min(

                float(trend),

                15

            )

        except:

            pass




        return round(

            min(

                score,

                100

            ),

            2

        )



    except Exception as e:


        logger.exception(e)


        return 0






def prepare_opportunity(
    item
):

    try:


        score = calculate_opportunity_score(
            item
        )



        item["opportunity_score"] = score



        return item



    except Exception as e:


        logger.exception(e)


        return None






def find_best_opportunities():

    try:


        opportunities = []



        symbols = get_symbols()



        if not symbols:


            logger.info(
                "NO SYMBOLS FOUND"
            )


            return []




        market_signals = analyze_market_symbols(

            symbols

        )



        if market_signals:


            opportunities.extend(

                market_signals

            )





        pumps = scan_advanced_pumps()



        if pumps:


            opportunities.extend(

                pumps

            )





        final = []



        for item in opportunities:



            prepared = prepare_opportunity(

                item

            )



            if not prepared:


                continue




            if prepared.get(

                "confidence",

                0

            ) < MIN_CONFIDENCE:


                continue




            final.append(

                prepared

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

            f"BEST OPPORTUNITIES: {len(final)}"

        )



        return final



    except Exception as e:


        logger.exception(e)


        return []
