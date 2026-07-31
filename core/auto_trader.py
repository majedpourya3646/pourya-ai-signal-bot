# core/auto_trader.py

from core.logger import logger

from core.opportunity_engine import (
    get_top_opportunity
)

from core.risk_engine import (
    validate_trade
)

from core.order_manager import (
    calculate_quantity,
    create_order
)

from core.trade_manager import (
    open_trade
)

from config import (
    INITIAL_BALANCE,
    LEVERAGE
)





def execute_auto_trade():

    try:


        opportunity = get_top_opportunity()



        if not opportunity:

            logger.info(

                "NO OPPORTUNITY FOUND"

            )

            return None





        if not validate_trade(

            opportunity

        ):

            logger.warning(

                "TRADE REJECTED BY RISK ENGINE"

            )

            return None






        symbol = opportunity.get(

            "symbol"

        )



        side = opportunity.get(

            "signal"

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





        quantity = calculate_quantity(

            INITIAL_BALANCE,

            entry,

            sl

        )





        if quantity <= 0:

            logger.warning(

                "INVALID QUANTITY"

            )

            return None







        order = create_order(

            symbol,

            side,

            quantity,

            LEVERAGE

        )





        if not order:

            logger.error(

                "ORDER FAILED"

            )

            return None






        trade_id = open_trade(

            symbol,

            side,

            entry,

            tp,

            sl,

            quantity,

            opportunity.get(

                "confidence",

                0

            )

        )





        if not trade_id:

            logger.error(

                "TRADE DATABASE FAILED"

            )

            return None





        result = {


            "trade_id":

                trade_id,



            "symbol":

                symbol,



            "side":

                side,



            "entry":

                entry,



            "tp":

                tp,



            "sl":

                sl,



            "quantity":

                quantity,



            "order":

                order

        }





        logger.info(

            f"AUTO TRADE OPENED {symbol}"

        )



        return result



    except Exception as e:


        logger.exception(e)


        return None







def scan_and_trade():

    try:


        return execute_auto_trade()



    except Exception as e:


        logger.exception(e)


        return None
