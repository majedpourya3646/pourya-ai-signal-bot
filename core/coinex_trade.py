# core/coinex_trade.py

from coinex_api import coinex

from core.logger import logger



class CoinExTrade:



    def open_long(
        self,
        symbol,
        quantity
    ):

        try:


            return coinex.create_order(

                market=symbol,

                side="buy",

                amount=quantity,

                order_type="market"

            )



        except Exception as e:


            logger.exception(
                e
            )


            return None




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
