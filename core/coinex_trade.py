# core/coinex_trade.py

from coinex_api import coinex

from core.logger import logger



class CoinExTrade:


    def create_order(
        self,
        symbol,
        side,
        quantity,
        leverage=None
    ):

        try:

            side = side.upper()


            if side not in [
                "BUY",
                "SELL"
            ]:

                logger.error(
                    f"INVALID SIDE {side}"
                )

                return None



            order_side = side.lower()



            logger.info(
                f"COINEX ORDER {symbol} {order_side} QTY={quantity}"
            )



            # Futures market order
            result = coinex.place_order(

                market=symbol,

                side=order_side,

                amount=str(quantity),

                order_type="market"

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
        symbol,
        side=None,
        quantity=None
    ):

        try:


            logger.info(
                f"CLOSE POSITION {symbol}"
            )


            return coinex.close_position(

                market=symbol

            )


        except Exception as e:


            logger.exception(e)

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

            logger.exception(e)

            return None






    def get_order_status(
        self,
        order_id
    ):

        try:

            return coinex.get_order(

                order_id

            )


        except Exception as e:

            logger.exception(e)

            return None






    def cancel_order(
        self,
        order_id,
        symbol=None
    ):

        try:

            return coinex.cancel_order(

                order_id

            )


        except Exception as e:

            logger.exception(e)

            return None





coinex_trade = CoinExTrade()
