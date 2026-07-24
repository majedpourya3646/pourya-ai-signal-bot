import json

from coinex_api import coinex

from core.logger import logger



class CoinExFuturesAPI:


    def _request(
        self,
        method,
        endpoint,
        params=None
    ):

        try:

            result = coinex._request(

                method,

                endpoint,

                params

            )


            logger.info(
                "FUTURES API RESPONSE"
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



    def get_futures_balance(
        self
    ):

        return self._request(

            "GET",

            "/assets/futures/balance"

        )



    def get_futures_positions(
        self
    ):

        return self._request(

            "GET",

            "/futures/pending-position"

        )



    def create_order(
        self,
        market,
        side,
        amount,
        order_type="market"
    ):

        try:

            return coinex.create_futures_order(

                market=market,

                side=side,

                amount=amount,

                order_type=order_type

            )


        except Exception as e:

            logger.exception(e)

            return None



coinex_futures = CoinExFuturesAPI()
