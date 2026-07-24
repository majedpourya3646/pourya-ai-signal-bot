# core/ai_analyzer.py

from signal_engine import analyze_signal

from multi_timeframe import analyze_symbol

from core.logger import logger



def analyze_with_ai(
    symbol
):

    try:


        result = analyze_symbol(
            symbol
        )



        if not result:

            return {

                "symbol": symbol,

                "decision": "WAIT",

                "reason": "No data"

            }



        confidence = result.get(
            "confidence",
            0
        )


        signal = result.get(
            "signal",
            "WAIT"
        )



        decision = "WAIT"



        if signal in [

            "BUY",

            "STRONG BUY"

        ] and confidence >= 70:


            decision = "BUY"



        elif signal in [

            "SELL",

            "STRONG SELL"

        ] and confidence >= 70:


            decision = "SELL"



        return {

            "symbol": symbol,

            "decision": decision,

            "signal": signal,

            "confidence": confidence,

            "entry": result.get(
                "entry"
            ),

            "tp": result.get(
                "tp"
            ),

            "sl": result.get(
                "sl"
            )

        }



    except Exception as e:


        logger.exception(
            e
        )


        return {

            "symbol": symbol,

            "decision": "WAIT",

            "error": str(e)

        }




def analyze_multiple_symbols(
    symbols
):

    results = []



    for symbol in symbols:


        result = analyze_with_ai(
            symbol
        )



        results.append(
            result
        )



    results.sort(

        key=lambda x: x.get(
            "confidence",
            0
        ),

        reverse=True

    )



    return results
