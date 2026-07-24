# coinex_futures_api.py

import json

from coinex_api import coinex

from core.logger import logger



class CoinExFuturesAPI:


    def _request(
        self,
        method,
        endpoint,
        params=None,
        body=None,
        private=True
    ):

        try:

            result = coinex._request(

                method,

                endpoint,

                params=params,

                body=body,

                private=private

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

            return {

                "code": -1,

                "message": str(e)

            }



    def get_futures_balance(self):

        return self._request(

            "GET",

            "/assets/futures/balance",

            private=True

        )



    def get_futures_positions(self):

        return self._request(

            "GET",

            "/futures/pending-position",

            private=True

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



    def close_position(
        self,
        market,
        side,
        amount
    ):

        close_side = (

            "sell"

            if side.upper() == "LONG"

            else "buy"

        )


        return self.create_order(

            market,

            close_side,

            amount

        )



coinex_futures = CoinExFuturesAPI()



# =====================================
# Compatibility functions
# برای فایل‌های قدیمی پروژه
# =====================================


def get_positions():

    result = coinex_futures.get_futures_positions()


    if not result:

        return []


    data = result.get(
        "data",
        []
    )


    if isinstance(data, dict):

        return data.get(
            "positions",
            []
        )


    return data



def get_balance():

    return coinex_futures.get_futures_balance()
