# core/coin_scanner.py

from core.logger import logger

from core.session import session

from config import (
    BASE_URL,
    MARKET_TYPE,
    REQUEST_TIMEOUT
)





def get_symbols():

    try:


        if MARKET_TYPE == "FUTURES":

            url = BASE_URL + "/futures/market"



        else:

            url = BASE_URL + "/spot/market"






        response = session.get(

            url,

            timeout=REQUEST_TIMEOUT

        )



        data = response.json()



        if data.get(

            "code"

        ) != 0:


            logger.error(

                f"MARKET LIST ERROR {data}"

            )


            return []






        markets = []



        items = data.get(

            "data",

            []

        )





        for item in items:


            symbol = item.get(

                "market"

            )



            if not symbol:

                continue



            if symbol.endswith(

                "USDT"

            ):


                markets.append(

                    symbol

                )







        return markets



    except Exception as e:


        logger.exception(e)


        return []









def get_active_symbols():

    try:


        symbols = get_symbols()



        return [

            x

            for x in symbols

            if x

        ]



    except Exception as e:


        logger.exception(e)


        return []
