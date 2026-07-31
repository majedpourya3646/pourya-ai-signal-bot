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


            if side not in [
                "buy",
                "sell"
            ]:

                logger.error(
                    f"INVALID SIDE {side}"
                )

                return None



            logger.info(
                f"COINEX ORDER {symbol} {side} QTY={quantity}"
            )



            params = {

                "market": symbol,

                "market_type": "FUTURES",

                "side": side,

                "type": "market",

                "amount": str(quantity)

            }



            result = coinex._request(

                "POST",

                "/futures/order",

                params

            )



            logger.info(
                f"COINEX RESPONSE {result}"
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


            params = {

                "market": symbol,

                "market_type": "FUTURES"

            }


            return coinex._request(

                "POST",

                "/futures/close-position",

                params

            )


        except Exception as e:

            logger.exception(e)

            return None




    def get_order(
        self,
        order_id
    ):

        try:


            return coinex._request(

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
        order_id,
        symbol=None
    ):

        try:


            params = {

                "order_id": order_id

            }


            if symbol:

                params["market"] = symbol



            return coinex._request(

                "POST",

                "/futures/cancel-order",

                params

            )


        except Exception as e:

            logger.exception(e)

            return None




coinex_trade = CoinExTrade()
