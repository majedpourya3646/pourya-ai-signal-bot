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


        if confidence >= 80:

            score += 50


        elif confidence >= 70:

            score += 40


        elif confidence >= 60:

            score += 30


        elif confidence >= 50:

            score += 15



        signal = item.get(
            "signal",
            ""
        )



        if signal == "STRONG BUY" or signal == "STRONG SELL":

            score += 30


        elif signal == "BUY" or signal == "SELL":

            score += 20



        timeframes = item.get(
            "timeframes",
            []
        )


        buy_count = 0

        sell_count = 0



        for tf in timeframes:

            tf_signal = tf.get(
                "signal",
                ""
            )


            if "BUY" in tf_signal:

                buy_count += 1


            elif "SELL" in tf_signal:

                sell_count += 1



        if buy_count >= 2:

            score += 15


        if sell_count >= 2:

            score += 15



        if buy_count == 0 and sell_count == 0:

            score -= 10



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





def validate_signal(
    item
):

    try:

        signal = item.get(
            "signal",
            ""
        )


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


        if signal not in [

            "BUY",

            "SELL",

            "STRONG BUY",

            "STRONG SELL"

        ]:

            return False



        if confidence < MIN_SIGNAL_SCORE:

            return False



        timeframes = item.get(
            "timeframes",
            []
        )


        if len(timeframes) < 3:

            return False



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



        if buy >= 2 or sell >= 2:

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


            signal["confidence"] = signal.get(
                "opportunity_score",
                0
            )



            if validate_signal(
                signal
            ):

                opportunities.append(
                    signal
                )



        for pump in pumps:


            if pump.get(
                "score",
                0
            ) < 70:

                continue



            opportunities.append(

                {

                    "symbol": pump.get(
                        "symbol"
                    ),

                    "signal": "PUMP WATCH",

                    "confidence": pump.get(
                        "score",
                        0
                    ),

                    "entry": None,

                    "tp": None,

                    "sl": None,

                    "opportunity_score": pump.get(
                        "score",
                        0
                    )

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
