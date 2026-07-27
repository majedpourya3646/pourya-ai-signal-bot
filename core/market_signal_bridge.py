# core/market_signal_bridge.py

from multi_timeframe import (
    analyze_symbol
)

from core.logger import logger

from datetime import datetime



VALID_SIGNALS = [
    "BUY",
    "SELL",
    "STRONG BUY",
    "STRONG SELL",
    "EARLY BUY",
    "EARLY SELL",
]


MIN_SCORE = 55



def is_valid_signal(result):

    try:

        signal = result.get(
            "signal",
            "WAIT"
        )

        score = result.get(
            "score",
            0
        )


        if signal not in VALID_SIGNALS:

            return False


        if score < MIN_SCORE:

            return False


        return True


    except Exception as e:

        logger.exception(e)

        return False





def normalize_signal(signal):

    try:

        mapping = {

            "STRONG BUY": "STRONG BUY",

            "STRONG SELL": "STRONG SELL",

            "BUY": "BUY",

            "SELL": "SELL",

            "EARLY BUY": "EARLY BUY",

            "EARLY SELL": "EARLY SELL",

        }


        return mapping.get(
            signal,
            "WAIT"
        )


    except Exception:

        return "WAIT"





def analyze_market_symbols(symbols):

    results = []


    try:


        for symbol in symbols:


            try:


                logger.info(
                    f"ANALYZING {symbol}"
                )



                result = analyze_symbol(
                    symbol
                )



                if not result:

                    continue



                logger.info(
                    f"{symbol} RESULT AFTER AI FILTER: {result}"
                )



                if not is_valid_signal(
                    result
                ):


                    logger.info(
                        f"{symbol} FILTERED OUT"
                    )

                    continue




                signal = normalize_signal(
                    result.get(
                        "signal",
                        "WAIT"
                    )
                )



                score = result.get(
                    "score",
                    result.get(
                        "confidence",
                        0
                    )
                )



                item = {


                    "symbol": symbol,


                    "market": "FUTURES",


                    "signal": signal,


                    "confidence": score,


                    "score": score,


                    "entry": result.get(
                        "entry",
                        result.get(
                            "price"
                        )
                    ),


                    "price": result.get(
                        "price"
                    ),


                    "tp": result.get(
                        "take_profit"
                    ),


                    "sl": result.get(
                        "stop_loss"
                    ),


                    "take_profit": result.get(
                        "take_profit"
                    ),


                    "stop_loss": result.get(
                        "stop_loss"
                    ),


                    "timeframes": result.get(
                        "timeframes",
                        []
                    ),


                    "grade": result.get(
                        "grade",
                        ""
                    ),


                    "reasons": result.get(
                        "reasons",
                        []
                    ),


                    "created_at": datetime.utcnow().isoformat()

                }



                results.append(
                    item
                )



                logger.info(
                    f"{symbol} ACCEPTED | {signal} | SCORE={score}"
                )



            except Exception as e:


                logger.error(
                    f"{symbol} ERROR {e}"
                )



        logger.info(
            f"VALID MARKET SIGNALS: {len(results)}"
        )



        return results



    except Exception as e:


        logger.exception(e)


        return []
