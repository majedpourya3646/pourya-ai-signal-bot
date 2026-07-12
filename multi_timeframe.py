from market import get_market_data
from signal_engine import analyze_market


def analyze_symbol(symbol):

    try:

        df_15m = get_market_data(symbol, interval="15")
        df_1h = get_market_data(symbol, interval="60")
        df_4h = get_market_data(symbol, interval="240")


        result_15m = analyze_market(df_15m)
        result_1h = analyze_market(df_1h)
        result_4h = analyze_market(df_4h)


        scores = [
            result_15m["confidence"],
            result_1h["confidence"],
            result_4h["confidence"]
        ]


        average_score = round(
            sum(scores) / 3
        )


        if (
            result_15m["signal"] in ["BUY", "STRONG BUY"]
            and
            result_1h["signal"] in ["BUY", "STRONG BUY"]
            and
            result_4h["signal"] in ["BUY", "STRONG BUY"]
        ):

            final_signal = "STRONG BUY"

        elif average_score >= 60:

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

        print(symbol, e)

        return {
            "signal": "WAIT",
            "entry": None,
            "tp": None,
            "sl": None,
            "confidence": 0,
            "detail": {}
        }
