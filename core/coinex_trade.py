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


            result = coinex.create_futures_order(

                market=symbol,

                side=order_side,

                amount=quantity

            )



            if not result:


                logger.error(
                    "EMPTY COINEX RESPONSE"
                )

                return None



            code = result.get(
                "code"
            )



            if code != 0:


                logger.error(
                    f"COINEX ORDER FAILED {result}"
                )

                return None



            logger.info(
                f"COINEX ORDER SUCCESS {result}"
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
        symbol
    ):


        try:


            result = coinex._request(

                "POST",

                "/futures/close-position",

                body={

                    "market":
                    symbol

                },

                private=True

            )


            if result.get("code") != 0:


                logger.error(
                    f"CLOSE FAILED {result}"
                )

                return None



            return result



        except Exception as e:


            logger.exception(e)

            return None





    def get_order(
        self,
        order_id,
        symbol
    ):


        try:


            return coinex._request(

                "GET",

                "/futures/order-status",

                params={

                    "market":
                    symbol,


                    "order_id":
                    order_id

                },

                private=True

            )


        except Exception as e:


            logger.exception(e)

            return None





    def cancel_order(
        self,
        order_id,
        symbol
    ):


        try:


            return coinex.cancel_order(

                order_id,

                symbol

            )


        except Exception as e:


            logger.exception(e)

            return None



coinex_trade = CoinExTrade()
