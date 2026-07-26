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





def discover_markets():

    try:

        response = session.get(
            MARKET_URL,
            timeout=20
        )


        logger.info(
            f"MARKET DISCOVERY URL: {MARKET_URL}"
        )


        logger.info(
            f"MARKET DISCOVERY STATUS: {response.status_code}"
        )


        data = response.json()



        if data.get(
            "code"
        ) != 0:

            logger.error(
                data
            )

            return []



        markets = data.get(
            "data",
            []
        )



        if not markets:

            return []



        logger.info(
            f"DISCOVERED MARKETS: {len(markets)}"
        )


        logger.info(
            f"MARKET SAMPLE: {markets[0]}"
        )



        return markets



    except Exception as e:

        logger.exception(e)

        return []
