# coinex_trade.py

from config import (
    PAPER_TRADING,
    ORDER_TYPE,
    LEVERAGE
)

from core.logger import logger
from coinex_api import coinex



class CoinExTrade:


    def create_order(
        self,
        market,
        side,
        amount,
        order_type=None,
        leverage=LEVERAGE
    ):

        try:


            if order_type is None:

                order_type = ORDER_TYPE



            side = side.lower()



            if side not in [
                "buy",
                "sell"
            ]:

                logger.error(
                    f"INVALID SIDE {side}"
                )

                return None




            logger.info(
                f"PAPER_TRADING={PAPER_TRADING}"
            )



            if PAPER_TRADING:


                logger.info(
                    f"PAPER ORDER | {side} | {market} | qty={amount}"
                )


                return {

                    "code": 0,

                    "message":
                    "Paper Trading",

                    "data": {

                        "market":
                        market,

                        "side":
                        side,

                        "amount":
                        amount,

                        "leverage":
                        leverage,

                        "order_id":
                        "PAPER"

                    }

                }




            logger.info(
                f"REAL ORDER | {side} | {market} | qty={amount}"
            )



            result = coinex.create_futures_order(

                market=market,

                side=side,

                amount=amount,

                order_type=order_type,

                leverage=leverage

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



            return result




        except Exception as e:


            logger.exception(e)


            return None





    def open_long(
        self,
        symbol,
        quantity
    ):


        return self.create_order(

            market=symbol,

            side="buy",

            amount=quantity

        )





    def open_short(
        self,
        symbol,
        quantity
    ):


        return self.create_order(

            market=symbol,

            side="sell",

            amount=quantity

        )





    def close_position(
        self,
        symbol,
        side,
        quantity
    ):


        close_side = (

            "sell"

            if side.upper() in [

                "BUY",

                "LONG"

            ]

            else

            "buy"

        )



        return self.create_order(

            market=symbol,

            side=close_side,

            amount=quantity

        )





coinex_trade = CoinExTrade()
