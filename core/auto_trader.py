# core/auto_trader.py

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    can_buy,
    open_trade
)

from core.risk_engine import (
    validate_trade
)

from core.portfolio import (
    INITIAL_BALANCE,
    get_trade_summary
)

from core.performance import (
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
            "signal",
            "WAIT"
        )


        if signal not in (
            "BUY",
            "STRONG BUY",
            "SELL",
            "STRONG SELL"
        ):

            return None



        if not can_buy(
            symbol
        ):

            logger.info(
                f"{symbol} already open"
            )

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



        if not all(
            [
                entry,
                tp,
                sl
            ]
        ):

            return None



        valid, result = validate_trade(

            INITIAL_BALANCE,

            INITIAL_BALANCE,

            {},

            entry,

            tp,

            sl

        )



        if not valid:

            logger.info(
                result
            )

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


        if quantity <= 0:

            return None



        if signal in (
            "BUY",
            "STRONG BUY"
        ):

            side = "LONG"

            order_side = "buy"


        else:

            side = "SHORT"

            order_side = "sell"




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



        open_trade(

            symbol=symbol,

            side=side,

            signal=signal,

            order_id=order_id,

            entry=entry,

            tp=tp,

            sl=sl,

            quantity=quantity,

            confidence=opportunity.get(
                "confidence",
                0
            )

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


        logger.info(
            f"{side} OPENED {symbol}"
        )


        return order



    except Exception as e:

        logger.exception(e)

        return None
