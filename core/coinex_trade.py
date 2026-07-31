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

            side = side.lower()

            logger.info(
                f"COINEX ORDER {symbol} {side} QTY={quantity}"
            )


            # CoinEx futures order endpoint
            result = coinex.request(
                "POST",
                "/futures/order",
                {
                    "market": symbol,
                    "side": side,
                    "type": "market",
                    "amount": quantity
                }
            )


            logger.info(
                f"COINEX RESULT {result}"
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
            "buy",
            quantity
        )





    def open_short(
        self,
        symbol,
        quantity
    ):

        return self.create_order(
            symbol,
            "sell",
            quantity
        )





    def close_position(
        self,
        symbol
    ):

        try:

            return coinex.request(
                "POST",
                "/futures/close-position",
                {
                    "market": symbol
                }
            )


        except Exception as e:

            logger.exception(e)

            return None






    def get_order(
        self,
        order_id
    ):

        try:

            return coinex.request(
                "GET",
                "/futures/order-status",
                {
                    "order_id": order_id
                }
            )


        except Exception as e:

            logger.exception(e)

            return None






    def cancel_order(
        self,
        order_id
    ):

        try:

            return coinex.request(
                "POST",
                "/futures/cancel-order",
                {
                    "order_id": order_id
                }
            )


        except Exception as e:

            logger.exception(e)

            return None



coinex_trade = CoinExTrade()
