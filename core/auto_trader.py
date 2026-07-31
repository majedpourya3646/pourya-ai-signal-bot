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
    MIN_CONFIDENCE,
    LEVERAGE
)





def execute_trade(signal):


    try:



        if not signal:


            return None






        symbol = signal.get(
            "symbol"
        )


        direction = signal.get(
            "signal"
        )



        confidence = signal.get(
            "confidence",
            0
        )



        entry = signal.get(
            "entry"
        )


        tp = signal.get(
            "tp"
        )


        sl = signal.get(
            "sl"
        )







        if confidence < MIN_CONFIDENCE:



            logger.info(

                f"TRADE REJECTED {symbol} CONF={confidence}"

            )


            return None







        if direction not in [

            "BUY",

            "SELL"

        ]:


            logger.info(

                f"INVALID SIGNAL {direction}"

            )


            return None







        logger.info(

            f"TRADE APPROVED {symbol} {direction}"

        )







        lot = calculate_lot(

            symbol

        )







        order = create_order(

            symbol,

            direction,

            lot,

            sl,

            tp

        )







        if not order:



            logger.error(

                "ORDER CREATION FAILED"

            )


            return None








        trade = {


            "symbol":

                symbol,


            "side":

                direction,


            "entry":

                entry,


            "tp":

                tp,


            "sl":

                sl,


            "confidence":

                confidence,


            "ticket":

                order.get(

                    "ticket"

                )



        }






        save_trade(

            trade

        )





        logger.info(

            f"TRADE OPENED {trade}"

        )





        return trade






    except Exception as e:


        logger.error(

            f"AUTO TRADER ERROR {e}"

        )


        return None









def calculate_lot(symbol):


    """
    محاسبه حجم معامله
    نسخه اولیه MT5
    """



    default_lot = 0.01



    return default_lot
