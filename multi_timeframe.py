from market import get_market_data
from signal_engine import analyze_market


def analyze_symbol(symbol):

    try:

        df_15m = get_market_data(symbol, interval="15")
        df_1h = get_market_data(symbol, interval="60")
        df_4h = get_market_data(symbol, interval="240")

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
                "reasons": [],
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
                score_15m * 0.40 +
                score_1h * 0.35 +
                score_4h * 0.25
            )
        )

        print(
            f"{symbol} | "
            f"15M: {score_15m} {result_15m['signal']} | "
            f"1H: {score_1h} {result_1h['signal']} | "
            f"4H: {score_4h} {result_4h['signal']} | "
            f"AVG: {average_score}"
        )

        bullish = 0

        for r in (result_15m, result_1h, result_4h):

            if r["signal"] in ["BUY", "STRONG BUY"]:
                bullish += 1

        if bullish >= 3 and average_score >= 70:

            final_signal = "STRONG BUY"

        elif bullish >= 2 and average_score >= 55:

            final_signal = "BUY"

        elif (
            result_15m["signal"] == "BUY"
            and result_1h["signal"] == "BUY"
            and average_score >= 50
        ):

            final_signal = "BUY"

        else:

            final_signal = "WAIT"

        reasons = (
            result_15m.get("reasons", [])
            + result_1h.get("reasons", [])
            + result_4h.get("reasons", [])
        )

        return {

            "signal": final_signal,

            "entry": result_15m["entry"],

            "tp": result_15m["tp"],

            "sl": result_15m["sl"],

            "confidence": average_score,

            "reasons": reasons,

            "detail": {

                "15m": result_15m,

                "1h": result_1h,

                "4h": result_4h

            }

        }

    except Exception as e:

        print("MULTI ERROR:", symbol, e)

        return {

            "signal": "WAIT",

            "entry": None,

            "tp": None,

            "sl": None,

            "confidence": 0,

            "reasons": [],

            "detail": {}

        }
