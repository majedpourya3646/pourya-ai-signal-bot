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
    "EARLY SELL"

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



    except Exception as e:


        logger.error(
            f"SIGNAL VALIDATION ERROR: {e}"
        )


        return False





def improve_final_signal(result):

    """
    تبدیل EARLY ها به فرصت قابل بررسی
    """

    try:


        signal = result.get(
            "signal",
            "WAIT"
        )


        timeframes = result.get(
            "timeframes",
            []
        )


        buy_votes = 0

        sell_votes = 0

        strong_votes = 0



        for tf in timeframes:


            tf_signal = tf.get(
                "signal",
                "WAIT"
            )


            tf_score = tf.get(
                "score",
                0
            )



            if tf_signal in [

                "BUY",
                "STRONG BUY",
                "EARLY BUY"

            ]:

                buy_votes += 1



            if tf_signal in [

                "SELL",
                "STRONG SELL",
                "EARLY SELL"

            ]:

                sell_votes += 1



            if tf_score >= 70:

                strong_votes += 1



        score = result.get(
            "score",
            0
        )



        # تقویت سیگنال صعودی

        if (

            signal == "WAIT"

            and buy_votes >= 2

            and score >= 60

        ):

            result["signal"] = "BUY"



        elif (

            signal == "EARLY BUY"

            and buy_votes >= 2

            and strong_votes >= 1

        ):

            result["signal"] = "BUY"





        # تقویت سیگنال نزولی


        elif (

            signal == "WAIT"

            and sell_votes >= 2

            and score >= 60

        ):

            result["signal"] = "SELL"



        elif (

            signal == "EARLY SELL"

            and sell_votes >= 2

            and strong_votes >= 1

        ):

            result["signal"] = "SELL"



        return result



    except Exception as e:


        logger.error(
            f"SIGNAL IMPROVEMENT ERROR: {e}"
        )


        return result






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



                result = improve_final_signal(
                    result
                )



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
