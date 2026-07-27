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
            "confidence",
            0
        )

        base_score = item.get(
            "score",
            0
        )

        timeframes = item.get(
            "timeframes",
            []
        )


        # -------------------------
        # Base AI SCORE
        # -------------------------

        score += base_score * 0.5


        # -------------------------
        # Confidence
        # -------------------------

        if confidence >= 80:
            score += 20

        elif confidence >= 65:
            score += 10



        # -------------------------
        # Signal strength
        # -------------------------

        if signal == "STRONG BUY":

            score += 20


        elif signal == "BUY":

            score += 12


        elif signal == "EARLY BUY":

            score += 10



        # -------------------------
        # Multi timeframe analysis
        # -------------------------

        bullish_frames = 0

        strong_frames = 0


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
                "STRONG BUY"
            ]:

                bullish_frames += 1


            if tf_score >= 70:

                strong_frames += 1



        if bullish_frames >= 3:

            score += 15


        elif bullish_frames == 2:

            score += 8



        if strong_frames >= 2:

            score += 10



        # -------------------------
        # Normalize
        # -------------------------

        if score > 100:

            score = 100


        return round(
            score,
            2
        )


    except Exception as e:

        logger.error(
            f"Opportunity score error: {e}"
        )

        return 0





def detect_signal_grade(score):

    if score >= 85:

        return "A+"


    elif score >= 75:

        return "A"


    elif score >= 65:

        return "B"


    elif score >= 50:

        return "C"


    else:

        return "D"





def improve_signal_type(item):

    """
    تبدیل WAIT های نزدیک به ورود
    به EARLY BUY
    """

    try:

        score = item.get(
            "score",
            0
        )


        timeframes = item.get(
            "timeframes",
            []
        )


        bullish = 0


        for tf in timeframes:

            if tf.get(
                "signal"
            ) in [
                "BUY",
                "STRONG BUY"
            ]:

                bullish += 1



        if (
            score >= 50
            and bullish >= 1
        ):

            item["signal"] = "EARLY BUY"



        return item


    except Exception as e:

        logger.error(
            f"Signal improvement error: {e}"
        )

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


            opportunity_score = calculate_opportunity_score(
                item
            )


            item["opportunity_score"] = opportunity_score


            item["grade"] = detect_signal_grade(
                opportunity_score
            )


            if opportunity_score >= 50:


                opportunities.append(
                    item
                )


        # Pump detection

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
                f"Pump scanner skipped: {e}"
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

        logger.error(
            f"Opportunity engine failed: {e}"
        )

        return []
        
def find_opportunities(limit=10):

    opportunities = find_best_opportunities()

    return opportunities[:limit]
