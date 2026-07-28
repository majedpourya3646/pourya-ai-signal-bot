# core/order_manager.py

from coinex_trade import coinex_trade

from core.config_manager import (
    get_setting
)

from core.logger import logger

from config import (
    LEVERAGE
)



def calculate_quantity(
    balance,
    price,
    stop_loss=None
):

    try:


        risk = float(
            get_setting(
                "risk_percent",
                1
            )
        )



        balance = float(
            balance
        )


        price = float(
            price
        )



        risk_amount = (

            balance

            *

            risk

            /

            100

        )



        if stop_loss:


            stop_loss = float(
                stop_loss
            )


            risk_distance = abs(

                price

                -

                stop_loss

            )


            if risk_distance > 0:


                quantity = (

                    risk_amount

                    /

                    risk_distance

                )

            else:


                quantity = (

                    risk_amount

                    /

                    price

                )



        else:


            quantity = (

                risk_amount

                /

                price

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
    quantity,
    leverage=LEVERAGE
):

    try:



        side = side.upper()



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


                "code":

                0,


                "status":

                "PAPER",


                "data":

                {


                    "symbol":

                    symbol,


                    "side":

                    side,


                    "quantity":

                    quantity,


                    "leverage":

                    leverage,


                    "order_id":

                    "PAPER"


                }


            }





        result = coinex_trade.create_order(

            market=symbol,

            side=side,

            amount=quantity,

            leverage=leverage

        )



        if not result:


            logger.error(

                "ORDER FAILED"

            )


            return None




        return result




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
