# core/market_intelligence.py

from core.logger import logger



def analyze_market_intelligence(
    opportunities
):

    try:

        if not opportunities:

            return {

                "trend": "UNKNOWN",

                "strength": 0,

                "count": 0

            }



        total_confidence = 0

        buy_count = 0

        sell_count = 0



        for item in opportunities:


            confidence = float(
                item.get(
                    "confidence",
                    0
                )
            )


            total_confidence += confidence



            signal = item.get(
                "signal",
                ""
            )


            if "BUY" in signal:

                buy_count += 1



            elif "SELL" in signal:

                sell_count += 1




        average = (

            total_confidence
            /
            len(opportunities)

        )



        if buy_count > sell_count:

            trend = "BULLISH"


        elif sell_count > buy_count:

            trend = "BEARISH"


        else:

            trend = "NEUTRAL"




        return {

            "trend": trend,

            "strength": round(
                average,
                2
            ),

            "count": len(
                opportunities
            ),

            "buy_signals": buy_count,

            "sell_signals": sell_count

        }



    except Exception as e:

        logger.exception(e)

        return {

            "trend": "ERROR",

            "strength": 0,

            "count": 0

        }
