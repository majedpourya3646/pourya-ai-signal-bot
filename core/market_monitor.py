# core/market_monitor.py

from core.coinex_connector import (
    get_market_price
)

from core.logger import logger



def monitor_market(
    symbol
):

    try:

        price = get_market_price(
            symbol
        )


        if not price:

            return None



        return {

            "symbol": symbol,

            "price": price

        }



    except Exception as e:

        logger.exception(e)

        return None





def monitor_symbols(
    symbols
):

    try:

        result = []


        for symbol in symbols:

            data = monitor_market(
                symbol
            )


            if data:

                result.append(
                    data
                )



        return result



    except Exception as e:

        logger.exception(e)

        return []
