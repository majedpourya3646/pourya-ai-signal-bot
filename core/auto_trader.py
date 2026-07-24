# core/auto_trader.py

from coinex_trade import coinex_trade

from trade_manager import (
    can_buy,
    open_trade
)

from portfolio import (
    INITIAL_BALANCE,
    get_trade_summary
)

from risk_manager import (
    validate_trade
)

from performance import (
    add_trade
)

from core.logger import logger



def execute_auto_trade(
    opportunity
):

    try:


        symbol = opportunity.get(
            "symbol"
        )


        signal = opportunity.get(
            "signal"
        )



        if signal not in [

            "BUY",

            "STRONG BUY"

        ]:

            return None



        if not can_buy(
            symbol
        ):

            return None



        entry = opportunity.get(
            "entry"
        )


        tp = opportunity.get(
            "tp"
        )


        sl = opportunity.get(
            "sl"
        )



        if not entry or not tp or not sl:

            return None



        valid, _ = validate_trade(

            INITIAL_BALANCE,

            INITIAL_BALANCE,

            {},

            entry,

            tp,

            sl

        )



        if not valid:

            return None



        summary = get_trade_summary(

            INITIAL_BALANCE,

            entry,

            tp,

            sl

        )



        quantity = summary.get(
            "quantity",
            0
        )



        order = coinex_trade.open_long(

            symbol,

            quantity

        )



        if not order:

            return None



        if order.get(
            "code"
        ) != 0:


            logger.error(
                order
            )


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



        open_trade(

            symbol,

            "buy",

            entry,

            quantity,

            opportunity.get(
                "confidence",
                0
            ),

            signal,

            order_id

        )



        add_trade(

            symbol,

            signal,

            entry,

            tp,

            sl,

            None,

            0,

            quantity,

            opportunity.get(
                "confidence",
                0
            ),

            opportunity.get(
                "grade",
                ""
            )

        )



        return order



    except Exception as e:


        logger.exception(
            e
        )


        return None
