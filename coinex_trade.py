import json

from config import (
    PAPER_TRADING,
    ORDER_TYPE
)

from core.logger import logger
from coinex_api import coinex



class CoinExTrade:


    def create_order(
        self,
        market,
        side,
        amount
    ):

        try:

            logger.info(
                f"PAPER_TRADING={PAPER_TRADING}"
            )


            if PAPER_TRADING:

                logger.info(
                    f"PAPER ORDER {side} {market} qty={amount}"
                )

                return {

                    "code": 0,

                    "message": "Paper Trading",

                    "data": {

                        "market": market,

                        "side": side,

                        "amount": amount,

                        "order_id": "PAPER"

                    }

                }



            logger.info(
                f"REAL ORDER {side} {market} qty={amount}"
            )


            result = coinex.create_futures_order(

                market=market,

                side=side,

                amount=amount,

                order_type=ORDER_TYPE

            )


            logger.info(
                "ORDER RESULT"
            )


            logger.info(

                json.dumps(

                    result,

                    ensure_ascii=False,

                    indent=2

                )

            )


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

            if side.upper() in (

                "BUY",
                "LONG"

            )

            else "buy"

        )


        return self.create_order(

            market=symbol,

            side=close_side,

            amount=quantity

        )



coinex_trade = CoinExTrade()
