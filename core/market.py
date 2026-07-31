# core/market.py

import requests

from core.logger import logger

from config import (
    BASE_URL,
    MARKET_TYPE,
    REQUEST_TIMEOUT
)





if MARKET_TYPE == "FUTURES":

    KLINE_URL = BASE_URL + "/futures/kline"

    TICKER_URL = BASE_URL + "/futures/ticker"


else:

    KLINE_URL = BASE_URL + "/spot/kline"

    TICKER_URL = BASE_URL + "/spot/ticker"








INTERVAL_MAP = {

    "15":

        "15min",


    "60":

        "1hour",


    "240":

        "4hour",


    "1D":

        "1day"

}








def get_market_data(
    symbol,
    interval="15",
    limit=200
):

    try:


        params = {


            "market":

                symbol,


            "period":

                INTERVAL_MAP.get(

                    interval,

                    "15min"

                ),


            "limit":

                limit

        }




        response = requests.get(

            KLINE_URL,

            params=params,

            timeout=REQUEST_TIMEOUT

        )



        data = response.json()



        if data.get(

            "code"

        ) != 0:


            logger.error(

                f"KLINE ERROR {data}"

            )


            return []





        candles = []



        for item in data.get(

            "data",

            []

        ):


            candles.append(

                {


                    "time":

                        item[0],



                    "open":

                        float(item[1]),



                    "close":

                        float(item[2]),



                    "high":

                        float(item[3]),



                    "low":

                        float(item[4]),



                    "volume":

                        float(item[5])

                }

            )



        return candles



    except Exception as e:


        logger.exception(e)


        return []









def get_latest_price(
    symbol
):

    try:


        params = {


            "market":

                symbol

        }



        response = requests.get(

            TICKER_URL,

            params=params,

            timeout=REQUEST_TIMEOUT

        )



        data = response.json()



        if data.get(

            "code"

        ) != 0:


            return None





        ticker = data.get(

            "data"

        )



        if isinstance(

            ticker,

            list

        ):

            ticker = ticker[0]





        return float(

            ticker.get(

                "last"

            )

        )



    except Exception as e:


        logger.exception(e)


        return None







def get_current_price(
    symbol
):

    return get_latest_price(

        symbol

    )
