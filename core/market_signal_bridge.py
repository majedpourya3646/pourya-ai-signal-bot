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
    "STRONG SELL"
]



MIN_SCORE = 60



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


    except Exception:

        return False




def analyze_market_symbols(
    symbols
):

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
                    f"{symbol} RESULT: {result}"
                )



                if not is_valid_signal(
                    result
                ):

                    logger.info(
                        f"{symbol} FILTERED OUT"
                    )

                    continue




                results.append(

                    {

                        "symbol": symbol,


                        "market": "FUTURES",


                        "signal": result.get(
                            "signal",
                            "WAIT"
                        ),


                        "confidence": result.get(
                            "score",
                            0
                        ),


                        "score": result.get(
                            "score",
                            0
                        ),


                        "entry": result.get(
                            "entry",
                            result.get(
                                "price"
                            )
                        ),


                        "tp": result.get(
                            "take_profit"
                        ),


                        "sl": result.get(
                            "stop_loss"
                        ),


                        "price": result.get(
                            "price"
                        ),


                        "timeframes": result.get(
                            "timeframes",
                            []
                        ),


                        "grade": result.get(
                            "grade",
                            ""
                        ),


                        "created_at": datetime.utcnow().isoformat()

                    }

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


        logger.exception(
            e
        )

        return []
