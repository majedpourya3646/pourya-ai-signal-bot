# core/coinex_trade.py

from coinex_api import coinex

from core.logger import logger



class CoinExTrade:



    def create_order(
        self,
        symbol,
        side,
        quantity
    ):

        try:

            if side in [
                "BUY",
                "LONG"
            ]:

                order_side = "buy"

            elif side in [
                "SELL",
                "SHORT"
            ]:

                order_side = "sell"

            else:

                logger.error(
                    f"INVALID ORDER SIDE {side}"
                )

                return None



            return coinex.create_order(

                market=symbol,

                side=order_side,

                amount=quantity,

                order_type="market"

            )



        except Exception as e:

            logger.exception(
                e
            )

            return None




    def open_long(
        self,
        symbol,
        quantity
    ):

        return self.create_order(

            symbol,

            "BUY",

            quantity

        )




    def open_short(
        self,
        symbol,
        quantity
    ):

        return self.create_order(

            symbol,

            "SELL",

            quantity

        )




    def close_position(
        self,
        symbol
    ):

        try:

            return coinex.close_position(

                market=symbol

            )



        except Exception as e:

            logger.exception(
                e
            )

            return None




    def get_order(
        self,
        order_id
    ):

        try:

            return coinex.get_order(
                order_id
            )



        except Exception as e:

            logger.exception(
                e
            )

            return None




    def cancel_order(
        self,
        order_id
    ):

        try:

            return coinex.cancel_order(
                order_id
            )



        except Exception as e:

            logger.exception(
                e
            )

            return None




coinex_trade = CoinExTrade()
