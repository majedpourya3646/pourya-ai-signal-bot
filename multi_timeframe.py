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


        signal_15m = analyze_market(df_15m)
        signal_1h = analyze_market(df_1h)
        signal_4h = analyze_market(df_4h)


        scores = [
            signal_15m["confidence"],
            signal_1h["confidence"],
            signal_4h["confidence"]
        ]


        average_score = round(
            sum(scores) / len(scores)
        )


        # تایید چند تایم فریم

        if (
            signal_15m["signal"] in ["BUY", "STRONG BUY"]
            and
            signal_1h["signal"] in ["BUY", "STRONG BUY"]
            and
            signal_4h["signal"] in ["BUY", "STRONG BUY"]
        ):

            final_signal = "STRONG BUY"


        elif average_score >= 60:

            final_signal = "BUY"


        else:

            final_signal = "WAIT"



        return {

            "signal": final_signal,

            "entry": signal_15m["entry"],

            "tp": signal_15m["tp"],

            "sl": signal_15m["sl"],

            "confidence": average_score

        }


    except Exception as e:

        print("Analyze error:", symbol, e)

        return {

            "signal": "WAIT",

            "entry": None,

            "tp": None,

            "sl": None,

            "confidence": 0

        }
