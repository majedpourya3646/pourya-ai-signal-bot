from signal_engine import analyze_signal
from market import get_market_data

from core.logger import logger


TIMEFRAMES = {
    "15": 0.25,
    "60": 0.35,
    "240": 0.40
}


def analyze_symbol(symbol):

    try:

        results = []

        total_score = 0
        total_weight = 0


        for timeframe, weight in TIMEFRAMES.items():

            df = get_market_data(
                symbol,
                interval=timeframe
            )


            if df.empty:
                continue


            result = analyze_signal(df)


            confidence = result.get(
                "confidence",
                0
            )


            signal = result.get(
                "signal",
                "WAIT"
            )


            total_score += confidence * weight
            total_weight += weight


            results.append(
                {
                    "timeframe": timeframe,
                    "signal": signal,
                    "confidence": confidence
                }
            )


        if total_weight == 0:

            return {
                "symbol": symbol,
                "signal": "WAIT",
                "confidence": 0,
                "timeframes": []
            }


        confidence = round(
            total_score / total_weight,
            2
        )


        tf15 = next(
            (
                x for x in results
                if x["timeframe"] == "15"
            ),
            None
        )


        tf60 = next(
            (
                x for x in results
                if x["timeframe"] == "60"
            ),
            None
        )


        tf240 = next(
            (
                x for x in results
                if x["timeframe"] == "240"
            ),
            None
        )


        signal = "WAIT"


        if (
            tf240
            and tf60
            and tf15
            and tf240["signal"] in ["BUY", "STRONG BUY"]
            and tf60["signal"] in ["BUY", "STRONG BUY"]
            and tf15["signal"] in ["BUY", "STRONG BUY"]
            and confidence >= 70
        ):

            signal = "STRONG BUY"


        elif confidence >= 60:

            signal = "BUY"



        return {

            "symbol": symbol,

            "signal": signal,

            "confidence": confidence,

            "timeframes": results,

            "entry": None,

            "tp": None,

            "sl": None

        }


    except Exception as e:

        logger.exception(e)


        return {

            "symbol": symbol,

            "signal": "WAIT",

            "confidence": 0

        }
