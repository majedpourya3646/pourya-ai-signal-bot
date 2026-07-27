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



def calculate_opportunity_score(item):

    try:

        score = 0


        confidence = float(
            item.get(
                "score",
                item.get(
                    "confidence",
                    0
                )
            )
            or 0
        )


        if confidence >= 75:
            score += 50

        elif confidence >= 60:
            score += 35

        elif confidence >= 45:
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



        buy = 0
        sell = 0


        for tf in item.get(
            "timeframes",
            []
        ):

            s = tf.get(
                "signal",
                ""
            )


            if "BUY" in s:
                buy += 1


            if "SELL" in s:
                sell += 1



        if buy >= 2:
            score += 20


        if sell >= 2:
            score += 20



        return min(
            score,
            100
        )


    except Exception as e:

        logger.exception(e)

        return 0





def validate_signal(item):

    try:

        score = float(
            item.get(
                "score",
                0
            )
        )


        if score < MIN_SIGNAL_SCORE:

            return False



        buy = 0
        sell = 0


        for tf in item.get(
            "timeframes",
            []
        ):


            signal = tf.get(
                "signal",
                ""
            )


            if "BUY" in signal:

                buy += 1


            elif "SELL" in signal:

                sell += 1



        if buy >= 2:

            item["signal"] = "EARLY BUY"

            return True



        if sell >= 2:

            item["signal"] = "EARLY SELL"

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



        signals = analyze_market_symbols(
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


                signal["confidence"] = signal[
                    "opportunity_score"
                ]


                opportunities.append(
                    signal
                )


            else:


                logger.info(
                    f"{signal.get('symbol')} FILTERED"
                )




        pumps = scan_advanced_pumps(
            symbols
        )



        for pump in pumps:


            if pump.get(
                "score",
                0
            ) >= 75:


                opportunities.append(

                    {

                        "symbol": pump.get(
                            "symbol"
                        ),

                        "signal": "PUMP WATCH",

                        "confidence": pump.get(
                            "score"
                        ),

                        "opportunity_score": pump.get(
                            "score"
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

                f"TOP {item['symbol']} | {item['signal']} | {item['opportunity_score']}"

            )



        return opportunities[:limit]



    except Exception as e:

        logger.exception(e)

        return []
