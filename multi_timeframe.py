from market import get_market_data
from signal_engine import analyze_market
from core.logger import logger


# وزن تایم‌فریم‌ها
# تایم بالاتر اهمیت بیشتری دارد
TIMEFRAME_WEIGHTS = {
    "15m": 0.20,
    "1h": 0.35,
    "4h": 0.45
}



def empty_result():

    return {
        "signal": "WAIT",
        "entry": None,
        "tp": None,
        "sl": None,
        "confidence": 0,
        "reasons": [],
        "detail": {}
    }



def analyze_symbol(symbol):

    try:

        # دریافت دیتا

        tf15 = get_market_data(
            symbol,
            interval="15"
        )


        tf1h = get_market_data(
            symbol,
            interval="60"
        )


        tf4h = get_market_data(
            symbol,
            interval="240"
        )



        if (
            tf15.empty
            or tf1h.empty
            or tf4h.empty
        ):

            logger.warning(
                f"{symbol} EMPTY DATA"
            )

            return empty_result()



        # تحلیل هر تایم فریم

        r15 = analyze_market(tf15)

        r1h = analyze_market(tf1h)

        r4h = analyze_market(tf4h)



        # محاسبه امتیاز نهایی

        score = round(

            r15["confidence"] *
            TIMEFRAME_WEIGHTS["15m"]

            +

            r1h["confidence"] *
            TIMEFRAME_WEIGHTS["1h"]

            +

            r4h["confidence"] *
            TIMEFRAME_WEIGHTS["4h"]

        )



        logger.info(

            f"{symbol} | "
            f"15M {r15['confidence']} {r15['signal']} | "
            f"1H {r1h['confidence']} {r1h['signal']} | "
            f"4H {r4h['confidence']} {r4h['signal']} | "
            f"AVG {score}"

        )



        results = [
            r15,
            r1h,
            r4h
        ]



        buy_count = sum(

            x["signal"] in [
                "BUY",
                "STRONG BUY"
            ]

            for x in results

        )



        strong_count = sum(

            x["signal"] == "STRONG BUY"

            for x in results

        )



        # منطق ورود

        if (
            buy_count == 3
            and score >= 70
        ):

            signal = "STRONG BUY"



        elif (
            buy_count >= 2
            and score >= 60
        ):

            signal = "BUY"



        else:

            signal = "WAIT"




        return {

            "signal": signal,

            "entry": r15.get(
                "entry"
            ),

            "tp": r15.get(
                "tp"
            ),

            "sl": r15.get(
                "sl"
            ),


            "confidence": score,


            "reasons": (
                r15.get(
                    "reasons",
                    []
                )
            ),



            "detail": {

                "15m": r15,

                "1h": r1h,

                "4h": r4h

            }

        }



    except Exception as e:


        logger.exception(

            f"MULTI ERROR {symbol}: {e}"

        )


        return empty_result()
