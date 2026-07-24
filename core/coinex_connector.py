# core/coinex_connector.py

from coinex_api import (
    coinex
)

from core.logger import logger



def check_connection():

    try:


        result = coinex.get_balance()



        if result.get(
            "code"
        ) == 0:


            return True



        return False



    except Exception as e:


        logger.exception(
            e
        )


        return False




def get_account_balance():

    try:


        result = coinex.get_balance()



        if result.get(
            "code"
        ) != 0:


            return {}



        return result.get(
            "data",
            {}
        )



    except Exception as e:


        logger.exception(
            e
        )


        return {}




def get_available_usdt():

    try:


        balance = get_account_balance()



        if not balance:

            return 0



        for item in balance:


            if item.get(
                "ccy"
            ) == "USDT":


                return float(

                    item.get(
                        "available",
                        0
                    )

                )



        return 0



    except Exception as e:


        logger.exception(
            e
        )


        return 0
