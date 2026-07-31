# core/trade_lifecycle_manager.py

from datetime import datetime

from core.logger import logger

from core.order_manager import (
    create_order
)

from core.trade_manager import (
    open_trade,
    close_trade
)

from core.position_manager import (
    calculate_pnl
)

from core.profit_manager import (
    calculate_user_trade_result
)

from core.notification_manager import (
    format_closed_trade_message
)





TRADE_STATUS = {


    "CREATED":

        "CREATED",


    "OPEN":

        "OPEN",


    "CLOSED":

        "CLOSED",


    "FAILED":

        "FAILED"

}








def create_trade_record(
    opportunity,
    quantity
):

    try:


        return {


            "symbol":

                opportunity.get(
                    "symbol"
                ),


            "side":

                opportunity.get(
                    "side"
                ),


            "entry":

                opportunity.get(
                    "entry"
                ),


            "tp":

                opportunity.get(
                    "tp"
                ),


            "sl":

                opportunity.get(
                    "sl"
                ),


            "quantity":

                quantity,


            "status":

                TRADE_STATUS["CREATED"],


            "created_at":

                datetime.utcnow()
                .isoformat()

        }



    except Exception as e:


        logger.exception(e)


        return None








def open_trade_cycle(
    opportunity,
    quantity,
    leverage
):

    try:


        symbol = opportunity.get(
            "symbol"
        )


        side = opportunity.get(
            "side"
        )



        order = create_order(

            symbol,

            side,

            quantity,

            leverage

        )



        if not order:


            logger.error(

                "ORDER CREATION FAILED"

            )


            return None



        saved = open_trade(

            symbol,

            side,

            opportunity.get(
                "entry"
            ),

            opportunity.get(
                "tp"
            ),

            opportunity.get(
                "sl"
            ),

            quantity,

            opportunity.get(
                "confidence",
                0
            )

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


            "status":

                TRADE_STATUS["OPEN"],


            "symbol":

                symbol,


            "side":

                side,


            "order":

                order

        }



    except Exception as e:


        logger.exception(e)


        return None








def close_trade_cycle(
    trade,
    exit_price,
    reason
):

    try:


        entry = float(

            trade.get(
                "entry",
                0
            )

        )


        quantity = float(

            trade.get(
                "quantity",
                0
            )

        )



        pnl = calculate_pnl(

            trade.get(
                "side"
            ),

            entry,

            exit_price,

            quantity

        )



        close_trade(

            trade.get(
                "id"
            )

        )



        result = calculate_user_trade_result(

            trade.get(
                "telegram_id"
            ),

            pnl

        )



        message = format_closed_trade_message(

            {

                "symbol":

                    trade.get(
                        "symbol"
                    ),


                "reason":

                    reason,


                "pnl":

                    pnl,


                "user_profit_percent":

                    trade.get(
                        "user_profit_percent",
                        50
                    )

            }

        )



        logger.info(

            message

        )



        return {


            "status":

                TRADE_STATUS["CLOSED"],


            "pnl":

                pnl,


            "profit_split":

                result,


            "message":

                message


        }



    except Exception as e:


        logger.exception(e)


        return None








def emergency_close_all(
    trades
):

    try:


        results = []



        for trade in trades:


            result = close_trade_cycle(

                trade,

                trade.get(
                    "current_price"
                ),

                "EMERGENCY CLOSE"

            )



            if result:

                results.append(
                    result
                )



        return results



    except Exception as e:


        logger.exception(e)


        return []
