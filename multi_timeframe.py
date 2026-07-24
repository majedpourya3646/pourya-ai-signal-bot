# multi_timeframe.py

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


        for timeframe, weight in TIMEFRAMES.items():

            df = get_market_data(

                symbol,

                interval=timeframe

            )


            if df.empty:

                continue


            result = analyze_signal(
                df
            )


            confidence = result.get(
                "confidence",
                0
            )


            total_score += (
                confidence * weight
            )


            results.append(

                {

                    "timeframe": timeframe,

                    "signal": result.get(
                        "signal",
                        "WAIT"
                    ),

                    "confidence": confidence

                }

            )


        confidence = round(
            total_score,
            2
        )


        if confidence >= 75:

            signal = "STRONG BUY"

        elif confidence >= 60:

            signal = "BUY"

        else:

            signal = "WAIT"



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

        logger.exception(
            e
        )


        return {

            "symbol": symbol,

            "signal": "WAIT",

            "confidence": 0

        }
