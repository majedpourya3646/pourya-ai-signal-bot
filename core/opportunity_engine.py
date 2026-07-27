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



MIN_SIGNAL_SCORE = 45



def calculate_opportunity_score(
    item
):

    try:

        score = 0


        confidence = float(
            item.get(
                "confidence",
                item.get(
                    "score",
                    0
                )
            )
            or 0
        )


        # confidence weight

        if confidence >= 85:

            score += 45

        elif confidence >= 75:

            score += 35

        elif confidence >= 65:

            score += 25

        elif confidence >= 55:

            score += 15



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



        timeframes = item.get(
            "timeframes",
            []
        )


        buy_count = 0

        sell_count = 0

        strong_count = 0



        for tf in timeframes:

            tf_signal = tf.get(
                "signal",
                ""
            )


            if "BUY" in tf_signal:

                buy_count += 1


            elif "SELL" in tf_signal:

                sell_count += 1



            if "STRONG" in tf_signal:

                strong_count += 1



        if buy_count >= 2:

            score += 20


        elif buy_count == 1:

            score += 10



        if sell_count >= 2:

            score += 20


        elif sell_count == 1:

            score += 10



        if strong_count >= 2:

            score += 10



        return max(
            0,
            min(
                score,
                100
            )
        )


    except Exception as e:

        logger.exception(e)

        return 0





def classify_opportunity(
    item
):

    try:

        score = item.get(
            "opportunity_score",
            0
        )


        signal = item.get(
            "signal",
            ""
        )


        timeframes = item.get(
            "timeframes",
            []
        )


        buy = 0

        sell = 0



        for tf in timeframes:

            tf_signal = tf.get(
                "signal",
                ""
            )


            if "BUY" in tf_signal:

                buy += 1


            elif "SELL" in tf_signal:

                sell += 1



        # A+ Entry

        if (

            score >= 75

            and

            (
                buy >= 2

                or

                sell >= 2

            )

        ):

            return "A+"



        # A Setup

        if (

            score >= 60

            and

            (
                buy >= 1

                or

                sell >= 1

            )

        ):

            return "A"



        # B Watch

        if score >= 45:

            return "B"



        return "C"



    except Exception as e:

        logger.exception(e)

        return "C"





def validate_signal(
    item
):

    try:

        opportunity_score = item.get(
            "opportunity_score",
            0
        )


        grade = item.get(
            "opportunity_grade",
            "C"
        )


        signal = item.get(
            "signal",
            ""
        )


        # حذف کامل WAIT انجام نمی‌شود

        if grade == "C":

            return False



        if opportunity_score < MIN_SIGNAL_SCORE:

            return False



        # سیگنال‌های واقعی

        if signal in [

            "BUY",

            "SELL",

            "STRONG BUY",

            "STRONG SELL"

        ]:

            return True



        # WAIT ولی آماده ورود

        if signal == "WAIT":

            timeframes = item.get(
                "timeframes",
                []
            )


            for tf in timeframes:

                tf_score = tf.get(
                    "score",
                    0
                )


                tf_signal = tf.get(
                    "signal",
                    ""
                )


                if (

                    tf_score >= 70

                    and

                    tf_signal != "WAIT"

                ):

                    return True



        return False



    except Exception as e:

        logger.exception(e)

        return False





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


            signal["opportunity_grade"] = classify_opportunity(
                signal
            )


            signal["confidence"] = max(

                float(
                    signal.get(
                        "confidence",
                        0
                    )
                    or 0
                ),

                signal["opportunity_score"]

            )



            if validate_signal(
                signal
            ):


                opportunities.append(
                    signal
                )



        for pump in pumps:


            pump_score = pump.get(
                "score",
                0
            )


            if pump_score < 70:

                continue



            opportunities.append(

                {

                    "symbol": pump.get(
                        "symbol"
                    ),

                    "signal": "PUMP WATCH",

                    "confidence": pump_score,

                    "entry": None,

                    "tp": None,

                    "sl": None,

                    "opportunity_score": pump_score,

                    "opportunity_grade": "A"

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
            f"FINAL OPPORTUNITIES: {len(opportunities)}"
        )



        for item in opportunities[:limit]:

            logger.info(

                f"TOP {item.get('symbol')} | "
                f"{item.get('signal')} | "
                f"GRADE {item.get('opportunity_grade')} | "
                f"SCORE {item.get('opportunity_score')}"

            )



        return opportunities[:limit]



    except Exception as e:

        logger.exception(e)

        return []
