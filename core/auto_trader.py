# core/auto_trader.py

from coinex_trade import coinex_trade

from portfolio import (
    get_trade_summary,
    INITIAL_BALANCE
)

from risk_manager import validate_trade

from trade_manager import (
    can_buy,
    open_trade,
    get_all_trades
)

from performance import add_trade

from core.signal_validator import validate_signal

from core.logger import logger



def execute_trade(
    symbol,
    analysis
):

    try:


        if not validate_signal(
            analysis
        ):

            return None



        if not can_buy(
            symbol
        ):

            return None



        entry = analysis.get(
            "entry"
        )


        tp = analysis.get(
            "tp"
        )


        sl = analysis.get(
            "sl"
        )



        if not entry or not tp or not sl:

            return None



        valid, size = validate_trade(

            INITIAL_BALANCE,

            INITIAL_BALANCE,

            get_all_trades(),

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



        if quantity <= 0:

            return None



        order = coinex_trade.open_long(

            symbol,

            quantity

        )



        if (

            not order

            or order.get("code") != 0

        ):


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

            analysis.get(
                "confidence",
                0
            ),

            analysis.get(
                "signal"
            ),

            order_id

        )



        add_trade(

            symbol,

            analysis.get(
                "signal"
            ),

            entry,

            tp,

            sl,

            None,

            0,

            quantity,

            analysis.get(
                "confidence",
                0
            ),

            analysis.get(
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
