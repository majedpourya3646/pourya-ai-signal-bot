# core/trade_executor.py

from core.order_manager import (
    create_order,
    close_order
)

from core.trade_manager import (
    open_trade,
    close_trade,
    get_trade
)

from core.logger import logger



def execute_open(
    symbol,
    side,
    quantity,
    entry,
    tp,
    sl,
    confidence=0,
    signal=""
):

    try:

        order_side = (
            "buy"
            if side == "LONG"
            else "sell"
        )


        order = create_order(

            symbol,

            order_side,

            quantity

        )


        if not order:

            return None



        order_id = (

            order.get(
                "data",
                {}
            )
            .get(
                "order_id"
            )

        )



        result = open_trade(

            symbol=symbol,

            side=side,

            signal=signal,

            order_id=order_id,

            entry=entry,

            tp=tp,

            sl=sl,

            quantity=quantity,

            confidence=confidence

        )


        if not result:

            return None



        return order



    except Exception as e:

        logger.exception(e)

        return None





def execute_close(
    symbol,
    price,
    reason="MANUAL"
):

    try:

        trade = get_trade(
            symbol
        )


        if not trade:

            return None



        order = close_order(
            symbol
        )


        if not order:

            return None



        result = close_trade(

            symbol,

            price,

            reason

        )


        if not result:

            return None



        return order



    except Exception as e:

        logger.exception(e)

        return None
