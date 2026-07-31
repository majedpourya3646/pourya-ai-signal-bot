# core/order_manager.py

from core.logger import logger

from coinex_trade import coinex_trade

from config import (
    RISK_PER_TRADE,
    INITIAL_BALANCE,
    PAPER_TRADING,
    ORDER_TYPE
)





def calculate_quantity(
    balance,
    entry,
    stop_loss
):

    try:


        if not balance or not entry or not stop_loss:

            return 0





        risk_amount = (

            float(balance)

            *

            float(RISK_PER_TRADE)

            /

            100

        )





        distance = abs(

            float(entry)

            -

            float(stop_loss)

        )





        if distance <= 0:

            return 0





        quantity = risk_amount / distance





        return round(

            quantity,

            6

        )



    except Exception as e:


        logger.exception(e)


        return 0










def validate_order_params(
    symbol,
    side,
    quantity
):

    try:


        if not symbol:

            return False



        if side not in [

            "BUY",

            "SELL"

        ]:

            return False



        if float(quantity) <= 0:

            return False



        return True



    except Exception:


        return False










def create_order(
    symbol,
    side,
    quantity,
    leverage=1
):

    try:


        if not validate_order_params(

            symbol,

            side,

            quantity

        ):

            logger.error(

                "INVALID ORDER PARAMS"

            )

            return None





        logger.info(

            f"CREATING ORDER {symbol} {side}"

        )





        if PAPER_TRADING:


            return {


                "status":

                    "PAPER",


                "symbol":

                    symbol,


                "side":

                    side,


                "quantity":

                    quantity,


                "type":

                    ORDER_TYPE,


                "leverage":

                    leverage

            }





        result = coinex_trade.create_order(

            symbol,

            side,

            quantity,

            leverage

        )



        if not result:


            logger.error(

                "EXCHANGE ORDER FAILED"

            )


            return None





        return result



    except Exception as e:


        logger.exception(e)


        return None










def close_order(
    symbol,
    side,
    quantity
):

    try:


        return coinex_trade.close_position(

            symbol,

            side,

            quantity

        )



    except Exception as e:


        logger.exception(e)


        return None










def get_balance():

    try:


        return coinex_trade.get_balance()



    except Exception as e:


        logger.exception(e)


        return None
