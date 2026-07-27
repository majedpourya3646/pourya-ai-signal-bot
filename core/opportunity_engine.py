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



def calculate_opportunity_score(item):

    try:

        score = 0


        signal = item.get(
            "signal",
            "WAIT"
        )


        confidence = item.get(
            "score",
            item.get(
                "confidence",
                0
            )
        )


        timeframes = item.get(
            "timeframes",
            []
        )


        # AI confidence

        score += confidence * 0.5



        if confidence >= 80:

            score += 20


        elif confidence >= 65:

            score += 10



        # Signal power

        if signal == "STRONG BUY":

            score += 20


        elif signal == "BUY":

            score += 15


        elif signal == "EARLY BUY":

            score += 10



        elif signal == "STRONG SELL":

            score += 20


        elif signal == "SELL":

            score += 15



        # Multi timeframe

        bullish = 0

        bearish = 0

        strong = 0



        for tf in timeframes:


            tf_signal = tf.get(
                "signal",
                "WAIT"
            )


            tf_score = tf.get(
                "score",
                0
            )


            if tf_signal in [
                "BUY",
                "STRONG BUY",
                "EARLY BUY"
            ]:

                bullish += 1



            if tf_signal in [
                "SELL",
                "STRONG SELL",
                "EARLY SELL"
            ]:

                bearish += 1



            if tf_score >= 70:

                strong += 1



        if bullish >= 3:

            score += 15


        elif bullish == 2:

            score += 8



        if bearish >= 3:

            score += 15


        elif bearish == 2:

            score += 8



        if strong >= 2:

            score += 10



        if score > 100:

            score = 100



        return round(
            score,
            2
        )


    except Exception as e:


        logger.exception(e)

        return 0




def calculate_grade(score):


    if score >= 85:

        return "A+"


    elif score >= 75:

        return "A"


    elif score >= 65:

        return "B"


    elif score >= 50:

        return "C"


    return "D"





def improve_signal_type(item):

    try:


        signal = item.get(
            "signal",
            "WAIT"
        )


        score = item.get(
            "score",
            0
        )


        timeframes = item.get(
            "timeframes",
            []
        )


        bullish = 0

        bearish = 0



        for tf in timeframes:


            tf_signal = tf.get(
                "signal",
                "WAIT"
            )


            if tf_signal in [
                "BUY",
                "STRONG BUY"
            ]:

                bullish += 1



            if tf_signal in [
                "SELL",
                "STRONG SELL"
            ]:

                bearish += 1



        if signal == "WAIT":


            if score >= 50 and bullish >= 1:

                item["signal"] = "EARLY BUY"



            elif score >= 50 and bearish >= 1:

                item["signal"] = "EARLY SELL"



        return item



    except Exception as e:


        logger.exception(e)

        return item





def find_best_opportunities():


    try:


        logger.info(
            "STARTING OPPORTUNITY ENGINE"
        )



        symbols = get_symbols()



        results = analyze_market_symbols(
            symbols
        )



        opportunities = []



        for item in results:


            item = improve_signal_type(
                item
            )



            opp_score = calculate_opportunity_score(
                item
            )


            item["opportunity_score"] = opp_score


            item["grade"] = calculate_grade(
                opp_score
            )



            if opp_score >= 50:


                opportunities.append(
                    item
                )



        # Pump scanner


        try:


            pumps = scan_advanced_pumps()



            for pump in pumps:


                pump["opportunity_score"] = 70

                pump["grade"] = "B"


                opportunities.append(
                    pump
                )



        except Exception as e:


            logger.warning(
                f"PUMP SCANNER ERROR: {e}"
            )



        opportunities.sort(
            key=lambda x: x.get(
                "opportunity_score",
                0
            ),
            reverse=True
        )



        logger.info(
            f"TOP OPPORTUNITIES FOUND: {len(opportunities)}"
        )



        for item in opportunities[:10]:


            logger.info(

                f"{item.get('symbol')} | "
                f"{item.get('signal')} | "
                f"SCORE={item.get('opportunity_score')} | "
                f"GRADE={item.get('grade')}"

            )



        return opportunities



    except Exception as e:


        logger.exception(e)

        return []





def find_opportunities(limit=10):


    opportunities = find_best_opportunities()


    return opportunities[:limit]
