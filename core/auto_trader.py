# core/auto_trader.py

from core.opportunity_engine import (
    calculate_opportunity_score
)

from core.risk_engine import (
    validate_trade
)

from core.order_manager import (
    create_order,
    calculate_quantity
)

from core.trade_manager import (
    open_trade
)

from core.logger import logger

from config import (
    INITIAL_BALANCE,
    LEVERAGE
)



def execute_opportunity(
    opportunity
):

    try:


        score = calculate_opportunity_score(
            opportunity
        )


        opportunity["confidence"] = score



        valid, reason = validate_trade(
            opportunity
        )


        if not valid:


            logger.info(
                f"TRADE REJECTED: {reason}"
            )


            return None




        symbol = opportunity.get(
            "symbol"
        )



        side = opportunity.get(
            "signal"
        )



        if side in [
            "STRONG BUY",
            "EARLY BUY"
        ]:

            side = "BUY"



        elif side in [
            "STRONG SELL",
            "EARLY SELL"
        ]:

            side = "SELL"



        if side not in [

            "BUY",

            "SELL"

        ]:


            logger.info(
                f"INVALID SIDE {side}"
            )


            return None





        entry = float(

            opportunity.get(

                "entry",

                opportunity.get(

                    "price",

                    0

                )

            )

        )



        if entry <= 0:


            logger.error(

                "INVALID ENTRY PRICE"

            )


            return None





        tp = opportunity.get(

            "tp",

            opportunity.get(

                "take_profit"

            )

        )



        sl = opportunity.get(

            "sl",

            opportunity.get(

                "stop_loss"

            )

        )





        quantity = opportunity.get(

            "quantity"

        )



        if not quantity:


            quantity = calculate_quantity(

                INITIAL_BALANCE,

                entry,

                sl

            )




        if quantity <= 0:


            logger.error(

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






        saved = open_trade(

            symbol,

            side,

            entry,

            tp,

            sl,

            quantity,

            score

        )



        if not saved:


            logger.error(

                "TRADE SAVE FAILED"

            )


            return None





        logger.info(

            f"TRADE OPENED {symbol} {side}"

        )



        return {


            "symbol":

            symbol,


            "side":

            side,


            "confidence":

            score,


            "quantity":

            quantity,


            "leverage":

            LEVERAGE,


            "tp":

            tp,


            "sl":

            sl,


            "order":

            order


        }





    except Exception as e:


        logger.exception(e)


        return None






def execute_batch(
    opportunities
):


    results = []



    try:



        if not opportunities:


            return []




        for item in opportunities:



            result = execute_opportunity(

                item

            )



            if result:


                results.append(

                    result

                )




        logger.info(

            f"EXECUTED TRADES: {len(results)}"

        )



        return results




    except Exception as e:


        logger.exception(e)


        return []
