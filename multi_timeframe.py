from market import get_market_data
from signal_engine import analyze_market


def analyze_symbol(symbol):

    try:

        df_15m = get_market_data(
            symbol,
            interval="15"
        )

        df_1h = get_market_data(
            symbol,
            interval="60"
        )

        df_4h = get_market_data(
            symbol,
            interval="240"
        )


        if (
            df_15m.empty
            or df_1h.empty
            or df_4h.empty
        ):

            return {
                "signal": "WAIT",
                "entry": None,
                "tp": None,
                "sl": None,
                "confidence": 0,
                "detail": {}
            }



        result_15m = analyze_market(df_15m)

        result_1h = analyze_market(df_1h)

        result_4h = analyze_market(df_4h)



        score_15m = result_15m["confidence"]

        score_1h = result_1h["confidence"]

        score_4h = result_4h["confidence"]



        average_score = round(
            (
                score_15m * 0.25
                +
                score_1h * 0.35
                +
                score_4h * 0.40
            )
        )



        print(
            symbol,
            "| 15M:",
            score_15m,
            result_15m["signal"],
            "| 1H:",
            score_1h,
            result_1h["signal"],
            "| 4H:",
            score_4h,
            result_4h["signal"],
            "| AVG:",
            average_score
        )



        bullish_count = 0


        for result in [
            result_15m,
            result_1h,
            result_4h
        ]:

            if result["signal"] in [
                "BUY",
                "STRONG BUY"
            ]:

                bullish_count += 1



        # ================= SMART FILTER =================


        higher_timeframe_ok = (
            result_4h["signal"] in [
                "BUY",
                "STRONG BUY"
            ]
        )


        medium_timeframe_ok = (
            result_1h["signal"] in [
                "BUY",
                "STRONG BUY"
            ]
        )


        short_timeframe_ok = (
            result_15m["signal"] in [
                "BUY",
                "STRONG BUY"
            ]
        )



        # ================= FINAL SIGNAL =================


        if (
            bullish_count == 3
            and
            average_score >= 70
        ):

            final_signal = "STRONG BUY"



        elif (
            higher_timeframe_ok
            and
            (medium_timeframe_ok or short_timeframe_ok)
            and
            average_score >= 45
        ):

            final_signal = "BUY"



        else:

            final_signal = "WAIT"



        return {

            "signal": final_signal,

            "entry": result_15m["entry"],

            "tp": result_15m["tp"],

            "sl": result_15m["sl"],

            "confidence": average_score,

            "detail": {

                "15m": result_15m,

                "1h": result_1h,

                "4h": result_4h

            }

        }



    except Exception as e:

        print(
            "MULTI ERROR:",
            symbol,
            e
        )


        return {

            "signal": "WAIT",

            "entry": None,

            "tp": None,

            "sl": None,

            "confidence": 0,

            "detail": {}

        }
