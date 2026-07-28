# core/market_discovery.py

from config import (
    BASE_URL,
    MARKET_TYPE
)

from core.session import session

from core.logger import logger





if MARKET_TYPE == "FUTURES":

    MARKET_URL = BASE_URL + "/futures/ticker"


else:

    MARKET_URL = BASE_URL + "/spot/ticker"







def normalize_market(
    item
):

    try:


        if not isinstance(
            item,
            dict
        ):

            return None




        symbol = item.get(
            "market",
            item.get(
                "symbol"
            )
        )



        if not symbol:

            return None





        volume = (

            item.get(
                "volume"
            )

            or

            item.get(
                "value"
            )

            or

            item.get(
                "turnover"
            )

            or 0

        )





        price = (

            item.get(
                "last"
            )

            or

            item.get(
                "close"
            )

            or 0

        )





        return {


            "symbol":

            str(symbol).upper(),


            "volume":

            float(volume),


            "price":

            float(price)


        }



    except Exception as e:


        logger.exception(e)


        return None







def discover_markets():

    try:



        logger.info(

            f"MARKET DISCOVERY URL: {MARKET_URL}"

        )




        response = session.get(

            MARKET_URL,

            timeout=20

        )





        logger.info(

            f"MARKET DISCOVERY STATUS: {response.status_code}"

        )





        if response.status_code != 200:


            logger.error(

                response.text

            )


            return []






        data = response.json()





        if data.get(

            "code"

        ) != 0:



            logger.error(

                data

            )


            return []







        raw_markets = data.get(

            "data",

            []

        )





        if isinstance(

            raw_markets,

            dict

        ):


            raw_markets = list(

                raw_markets.values()

            )






        markets = []





        for item in raw_markets:



            normalized = normalize_market(

                item

            )



            if normalized:


                markets.append(

                    normalized

                )







        logger.info(

            f"DISCOVERED MARKETS: {len(markets)}"

        )





        if markets:


            logger.info(

                f"MARKET SAMPLE: {markets[0]}"

            )





        return markets





    except Exception as e:


        logger.exception(e)


        return []
