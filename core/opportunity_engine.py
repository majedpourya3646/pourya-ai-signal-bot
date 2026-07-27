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



MIN_SCORE_TRADE = 70
MIN_SCORE_WATCH = 50



def calculate_opportunity_score(item):

    try:

        score = 0


        signal_score = float(
            item.get(
                "score",
                0
            )
            or 0
        )


        # Technical confidence

        if signal_score >= 80:

            score += 50


        elif signal_score >= 70:

            score += 40


        elif signal_score >= 60:

            score += 30


        elif signal_score >= 50:

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



        timeframes = item.get(
            "timeframes",
            []
        )


        has_4h = False
        has_1h = False
        has_15m = False


        buy_count = 0
        sell_count = 0



        for tf in timeframes:


            timeframe = str(
                tf.get(
                    "timeframe",
                    ""
                )
            )


            tf_signal = tf.get(
                "signal",
                ""
            )



            if timeframe in [
                "240",
                "4h"
            ]:

                has_4h = True



            if timeframe in [
                "60",
                "1h"
            ]:

                has_1h = True



            if timeframe in [
                "15"
            ]:

                has_15m = True



            if "BUY" in tf_signal:

                buy_count += 1



            elif "SELL" in tf_signal:

                sell_count += 1



        # Multi timeframe bonus

        if buy_count >= 2:

            score += 15


        if sell_count >= 2:

            score += 15



        # Higher timeframe confirmation

        if has_4h and has_1h:

            score += 10



        return min(
            score,
            100
        )



    except Exception as e:

        logger.exception(e)

        return 0




def classify_opportunity(item):

    try:

        score = item.get(
            "opportunity_score",
            0
        )


        signal = item.get(
            "signal",
            ""
        )


        if signal in [
            "STRONG BUY",
            "STRONG SELL"
        ] and score >= MIN_SCORE_TRADE:

            return "TRADE"



        if score >= MIN_SCORE_TRADE:

            return "TRADE"



        if score >= MIN_SCORE_WATCH:

            return "WATCH"



        return "IGNORE"



    except Exception as e:

        logger.exception(e)

        return "IGNORE"




def validate_signal(item):

    try:

        signal = item.get(
            "signal",
            ""
        )


        score = float(
            item.get(
                "score",
                0
            )
            or 0
        )


        if signal not in [

            "BUY",

            "SELL",

            "STRONG BUY",

            "STRONG SELL"

        ]:

            return False



        if score < 60:

            return False



        return True



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


        opportunities = []



        for signal in signals:


            signal["opportunity_score"] = calculate_opportunity_score(
                signal
            )


            signal["status"] = classify_opportunity(
                signal
            )



            if signal["status"] != "IGNORE":

                opportunities.append(
                    signal
                )



        for pump in pumps:


            pump_score = pump.get(
                "score",
                0
            )


            if pump_score >= 70:


                opportunities.append(

                    {

                        "symbol": pump.get(
                            "symbol"
                        ),

                        "signal": "PUMP WATCH",

                        "score": pump_score,

                        "confidence": pump_score,

                        "opportunity_score": pump_score,

                        "status": "WATCH",

                        "entry": None,

                        "tp": None,

                        "sl": None

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

                f"{item.get('symbol')} | "
                f"{item.get('signal')} | "
                f"{item.get('status')} | "
                f"SCORE={item.get('opportunity_score')}"

            )



        return opportunities[:limit]



    except Exception as e:

        logger.exception(e)

        return []
