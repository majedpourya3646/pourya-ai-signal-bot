# core/coinex_monitor.py

from coinex_trade import coinex_trade

from core.logger import logger





def get_account_balance():

    try:

        result = coinex_trade.get_balance()



        if not result:

            return None



        if result.get(
            "code"
        ) != 0:

            logger.error(
                result
            )

            return None



        return result.get(
            "data",
            {}
        )



    except Exception as e:

        logger.exception(e)

        return None





def get_position_status(
    symbol
):

    try:

        result = coinex_trade.get_position(
            symbol
        )



        if not result:

            return None



        if result.get(
            "code"
        ) != 0:

            return None



        return result.get(
            "data",
            {}
        )



    except Exception as e:

        logger.exception(e)

        return None





def check_exchange_connection():

    try:

        balance = get_account_balance()



        if balance is None:

            return False



        return True



    except Exception as e:

        logger.exception(e)

        return False





def exchange_status():

    try:

        return {

            "connected": check_exchange_connection(),

            "exchange": "CoinEx"

        }



    except Exception as e:

        logger.exception(e)

        return {

            "connected": False

        }
