# core/auto_trader.py

from core.logger import logger


from core.order_manager import (
    create_order
)


from core.trade_manager import (
    save_trade
)


from config import (

    MAX_OPEN_TRADES,

    MIN_CONFIDENCE

)







def execute_trade(

    opportunity

):


    try:



        if not opportunity:


            logger.info(

                "NO OPPORTUNITY"

            )


            return None







        symbol = opportunity.get(

            "symbol"

        )



        signal = opportunity.get(

            "signal"

        )



        confidence = opportunity.get(

            "confidence",

            0

        )



        entry = opportunity.get(

            "entry"

        )



        tp = opportunity.get(

            "tp"

        )



        sl = opportunity.get(

            "sl"

        )







        logger.info(

            f"TRADE CHECK {symbol} {signal} CONF={confidence}"

        )







        if confidence < MIN_CONFIDENCE:



            logger.info(

                f"TRADE REJECTED {symbol} CONF={confidence}"

            )


            return None








        result = create_order(

            symbol,

            signal,

            entry,

            tp,

            sl

        )








        if not result:



            logger.error(

                "ORDER CREATION FAILED"

            )


            return None








        trade_id = save_trade(

            {


                "symbol":

                    symbol,


                "side":

                    signal,


                "entry":

                    entry,


                "tp":

                    tp,


                "sl":

                    sl,


                "ticket":

                    result.get(

                        "ticket"

                    ),


                "status":

                    "OPEN"



            }

        )







        logger.info(

            f"TRADE OPENED {trade_id}"

        )





        return {


            "trade_id":

                trade_id,


            "order":

                result



        }







    except Exception as e:



        logger.error(

            f"AUTO TRADER ERROR {e}"

        )


        return None













def auto_trade(

    opportunities

):


    try:



        if not opportunities:


            return None







        sorted_items = sorted(

            opportunities,

            key=lambda x:

                x.get(

                    "confidence",

                    0

                ),

            reverse=True

        )







        best = sorted_items[0]





        logger.info(

            f"BEST TRADE {best}"

        )



        return execute_trade(

            best

        )






    except Exception as e:



        logger.error(

            f"AUTO TRADE LOOP ERROR {e}"

        )


        return None
