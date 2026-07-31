# core/order_manager.py

from datetime import datetime

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

        risk_percent = float(
            get_setting(
                "risk_percent",
                1
            )
        )

        balance = float(balance)
        price = float(price)

        if balance <= 0 or price <= 0:
            return 0


        risk_amount = (
            balance *
            risk_percent /
            100
        )


        if stop_loss:

            stop_loss = float(stop_loss)

            risk_distance = abs(
                price -
                stop_loss
            )


            if risk_distance > 0:

                quantity = (
                    risk_amount /
                    risk_distance
                )

            else:

                quantity = (
                    risk_amount /
                    price
                )


        else:

            quantity = (
                risk_amount /
                price
            )


        if quantity <= 0:
            return 0


        return round(
            quantity,
            6
        )


    except Exception as e:

        logger.exception(e)

        return 0



def validate_order(
    symbol,
    side,
    quantity
):

    try:

        if not symbol:

            return False


        side = side.upper()


        if side not in [
            "BUY",
            "SELL"
        ]:

            logger.error(
                f"INVALID SIDE {side}"
            )

            return False



        if float(quantity) <= 0:

            logger.error(
                f"INVALID QUANTITY {quantity}"
            )

            return False



        return True


    except Exception as e:

        logger.exception(e)

        return False



def create_order(
    symbol,
    side,
    quantity,
    leverage=LEVERAGE,
    stop_loss=None,
    take_profit=None
):

    try:


        if not validate_order(
            symbol,
            side,
            quantity
        ):

            return None



        side = side.upper()



        paper = get_setting(
            "paper_trading",
            True
        )


        order_time = datetime.utcnow().isoformat()



        if paper:


            order = {


                "code": 0,


                "status": "PAPER",


                "created_at": order_time,


                "data": {

                    "symbol": symbol,

                    "side": side,

                    "quantity": quantity,

                    "leverage": leverage,

                    "stop_loss": stop_loss,

                    "take_profit": take_profit,

                    "order_id": "PAPER"

                }

            }


            logger.info(
                f"PAPER ORDER CREATED | {symbol} | {side} | {quantity}"
            )


            return order



        logger.info(
            f"REAL ORDER REQUEST | {symbol} | {side} | {quantity}"
        )



        result = coinex_trade.create_order(

            market=symbol,

            side=side,

            amount=quantity,

            leverage=leverage

        )



        if not result:


            logger.error(
                f"ORDER FAILED | {symbol}"
            )


            return None



        result["created_at"] = order_time



        logger.info(
            f"ORDER SUCCESS | {symbol} | {side}"
        )


        return result



    except Exception as e:


        logger.exception(e)


        return None



def cancel_order(
    order_id,
    symbol
):

    try:


        if not order_id or not symbol:

            return False



        result = coinex_trade.cancel_order(

            order_id,

            symbol

        )


        if result:

            logger.info(
                f"ORDER CANCELLED | {symbol} | {order_id}"
            )


        return result



    except Exception as e:


        logger.exception(e)


        return False



def get_order_status(
    order_id,
    symbol
):

    try:


        result = coinex_trade.get_order_status(

            order_id,

            symbol

        )


        return result



    except Exception as e:


        logger.exception(e)


        return None
