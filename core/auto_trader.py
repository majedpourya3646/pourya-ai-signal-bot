# core/auto_trader.py


from core.logger import logger


from core.order_manager import (
    create_order
)


from core.trade_manager import (
    save_trade
)


from config import (
    MIN_CONFIDENCE,
    MAX_OPEN_TRADES
)






def execute_trade(

    opportunity

):


    try:



        if not opportunity:


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

            f"TRADE CHECK {symbol} CONF={confidence}"

        )








        if confidence < MIN_CONFIDENCE:



            logger.info(

                f"TRADE REJECTED {symbol} LOW CONFIDENCE"

            )


            return None







        open_trades = save_trade.get_open_trades()




        if len(open_trades) >= MAX_OPEN_TRADES:



            logger.info(

                "MAX OPEN TRADES REACHED"

            )


            return None








        logger.info(

            f"TRADE APPROVED {symbol}"

        )








        order = create_order(

            symbol,

            signal,

            entry,

            tp,

            sl

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

                signal,


            "entry":

                entry,


            "tp":

                tp,


            "sl":

                sl,


            "confidence":

                confidence,


            "status":

                "OPEN"


        }







        save_trade(

            trade

        )







        logger.info(

            f"TRADE SAVED {symbol}"

        )




        return trade







    except Exception as e:



        logger.error(

            f"AUTO TRADER ERROR {e}"

        )


        return None
