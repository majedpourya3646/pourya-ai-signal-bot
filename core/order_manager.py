# core/order_manager.py

from coinex_trade import coinex_trade

from core.config_manager import (
    get_setting
)

from core.logger import logger



def calculate_quantity(
    balance,
    price
):

    try:

        risk = get_setting(
            "risk_percent",
            1
        )


        amount = (
            float(balance)
            *
            float(risk)
            /
            100
        )


        quantity = (
            amount
            /
            float(price)
        )


        return round(
            quantity,
            6
        )


    except Exception as e:

        logger.exception(e)

        return 0




def create_order(
    symbol,
    side,
    quantity
):

    try:

        if side not in [
            "BUY",
            "SELL"
        ]:

            logger.error(
                f"INVALID ORDER SIDE: {side}"
            )

            return None



        paper = get_setting(
            "paper_trading",
            True
        )



        if paper:

            logger.info(
                f"PAPER ORDER {symbol} {side} {quantity}"
            )


            return {

                "status": "PAPER",

                "symbol": symbol,

                "side": side,

                "quantity": quantity

            }




        result = coinex_trade.create_order(

            symbol,

            side,

            quantity

        )



        if not result:

            logger.error(
                "EMPTY ORDER RESPONSE"
            )

            return None



        if result.get(
            "code"
        ) != 0:

            logger.error(
                result
            )

            return None



        return result.get(
            "data"
        )



    except Exception as e:

        logger.exception(e)

        return None




def cancel_order(
    order_id,
    symbol
):

    try:

        result = coinex_trade.cancel_order(

            order_id,

            symbol

        )


        return result



    except Exception as e:

        logger.exception(e)

        return False
