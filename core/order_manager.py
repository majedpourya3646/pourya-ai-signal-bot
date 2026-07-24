# core/order_manager.py

from coinex_trade import coinex_trade

from core.logger import logger



def create_order(
    symbol,
    side,
    quantity,
    order_type="market"
):

    try:


        if side.lower() == "buy":


            result = coinex_trade.open_long(

                symbol,

                quantity

            )



        elif side.lower() == "sell":


            result = coinex_trade.close_position(

                symbol

            )



        else:


            return None



        if not result:


            return None



        if result.get(
            "code"
        ) != 0:


            logger.error(
                result
            )


            return None



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return None




def get_order_status(
    order_id
):

    try:


        result = coinex_trade.get_order(

            order_id

        )



        if not result:


            return None



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return None




def cancel_order(
    order_id
):

    try:


        result = coinex_trade.cancel_order(

            order_id

        )



        if result.get(
            "code"
        ) == 0:


            return True



        return False



    except Exception as e:


        logger.exception(
            e
        )


        return False
