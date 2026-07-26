# core/auto_trader.py

from core.opportunity_engine import (
    calculate_opportunity_score
)

from core.risk_engine import (
    validate_trade
)

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    open_trade
)

from core.logger import logger



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


        if side not in [
            "BUY",
            "SELL"
        ]:

            logger.info(
                f"INVALID SIDE {side}"
            )

            return None



        quantity = opportunity.get(
            "quantity",
            0
        )


        entry = opportunity.get(
            "entry",
            opportunity.get(
                "price"
            )
        )


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



        order = create_order(

            symbol,

            side,

            quantity

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
            f"TRADE OPENED {symbol}"
        )



        return {

            "symbol": symbol,

            "side": side,

            "confidence": score,

            "order": order

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
