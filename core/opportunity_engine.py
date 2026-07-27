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



# =========================================
# OPPORTUNITY ENGINE V2
# AI Opportunity Ranking System
# =========================================



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



        # -------------------------
        # AI CONFIDENCE
        # -------------------------

        score += confidence * 0.55



        if confidence >= 90:

            score += 20


        elif confidence >= 80:

            score += 15


        elif confidence >= 70:

            score += 10




        # -------------------------
        # SIGNAL QUALITY
        # -------------------------

        if signal in [
            "STRONG BUY",
            "STRONG SELL"
        ]:

            score += 25



        elif signal in [
            "BUY",
            "SELL"
        ]:

            score += 15



        elif signal in [
            "EARLY BUY",
            "EARLY SELL"
        ]:

            score += 5




        # -------------------------
        # MULTI TIMEFRAME CONFIRM
        # -------------------------

        bullish = 0

        bearish = 0

        strong_tf = 0



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



            elif tf_signal in [
                "SELL",
                "STRONG SELL",
                "EARLY SELL"
            ]:

                bearish += 1



            if tf_score >= 75:

                strong_tf += 1




        if bullish >= 3:

            score += 15


        elif bullish == 2:

            score += 8



        if bearish >= 3:

            score += 15


        elif bearish == 2:

            score += 8




        if strong_tf >= 2:

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


    elif score >= 55:

        return "C"


    return "D"






def is_trade_ready(item):

    try:


        signal = item.get(
            "signal",
            "WAIT"
        )


        score = item.get(
            "score",
            0
        )


        grade = item.get(
            "grade",
            "D"
        )



        valid_signals = [

            "BUY",

            "SELL",

            "STRONG BUY",

            "STRONG SELL"

        ]



        if signal not in valid_signals:

            return False



        if score < 60:

            return False



        if grade == "D":

            return False



        return True



    except Exception:


        return False






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


            item["opportunity_score"] = calculate_opportunity_score(
                item
            )


            item["grade"] = calculate_grade(
                item["opportunity_score"]
            )



            if is_trade_ready(
                item
            ):


                opportunities.append(
                    item
                )




        # -------------------------
        # Advanced Pump Scanner
        # -------------------------

        try:


            pumps = scan_advanced_pumps()



            for pump in pumps:


                pump_score = calculate_opportunity_score(
                    pump
                )


                pump["opportunity_score"] = pump_score


                pump["grade"] = calculate_grade(
                    pump_score
                )



                if pump_score >= 65:


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
