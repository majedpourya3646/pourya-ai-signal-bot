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



MIN_SIGNAL_SCORE = 60
MIN_OPPORTUNITY_SCORE = 70



def calculate_opportunity_score(item):

    try:

        score = 0


        confidence = float(
            item.get(
                "score",
                0
            )
            or 0
        )


        if confidence >= 80:

            score += 50

        elif confidence >= 70:

            score += 40

        elif confidence >= 60:

            score += 30



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


            if timeframe == "240":

                if "BUY" in tf_signal or "SELL" in tf_signal:

                    score += 15



            elif timeframe in [
                "60",
                "1h"
            ]:

                if "BUY" in tf_signal or "SELL" in tf_signal:

                    score += 10



        return min(
            score,
            100
        )


    except Exception as e:

        logger.exception(e)

        return 0




def validate_signal(item):

    try:

        signal = item.get(
            "signal",
            ""
        )


        confidence = float(
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



        if confidence < MIN_SIGNAL_SCORE:

            return False



        opportunity = item.get(
            "opportunity_score",
            0
        )


        if opportunity < MIN_OPPORTUNITY_SCORE:

            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False




def find_opportunities(limit=20):

    try:

        symbols = get_symbols()


        logger.info(
            f"TOTAL SYMBOLS: {len(symbols)}"
        )


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
                f"TOP {item.get('symbol')} | {item.get('signal')} | SCORE {item.get('opportunity_score')}"
            )


        return opportunities[:limit]



    except Exception as e:

        logger.exception(e)

        return []
