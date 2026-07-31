# core/order_manager.py

from core.logger import logger

from core.coinex_trade import (
    coinex_trade
)

from config import (
    PAPER_TRADING
)







def create_order(
    symbol,
    side,
    quantity
):

    try:


        logger.info(
            f"CREATING ORDER {symbol} {side}"
        )



        if PAPER_TRADING:


            logger.info(
                f"PAPER ORDER | {symbol} | {side} | {quantity}"
            )


            return {

                "status":

                    "success",


                "mode":

                    "paper",


                "symbol":

                    symbol,


                "side":

                    side,


                "quantity":

                    quantity

            }







        result = coinex_trade.create_order(

            symbol,

            side,

            quantity

        )





        if not result:


            logger.error(
                "COINEX ORDER FAILED"
            )


            return None





        logger.info(
            f"LIVE ORDER CREATED {result}"
        )


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


        logger.info(
            f"CLOSING ORDER {symbol}"
        )





        if PAPER_TRADING:


            logger.info(
                f"PAPER CLOSE | {symbol}"
            )


            return True






        result = coinex_trade.close_position(

            symbol,

            side,

            quantity

        )





        if result:


            logger.info(
                f"POSITION CLOSED {symbol}"
            )


            return True





        return False





    except Exception as e:


        logger.exception(e)


        return False










def validate_order(
    symbol,
    quantity
):

    try:


        if not symbol:

            return False





        if float(quantity) <= 0:

            return False





        return True





    except Exception as e:


        logger.exception(e)


        return False










def get_order_status(
    order_id
):

    try:


        if PAPER_TRADING:


            return {

                "status":

                    "filled"

            }





        return coinex_trade.get_order_status(

            order_id

        )





    except Exception as e:


        logger.exception(e)


        return None
