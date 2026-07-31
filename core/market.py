# core/market.py

import requests

import pandas as pd

from core.logger import logger

from config import (
    BASE_URL,
    MARKET_TYPE,
    REQUEST_TIMEOUT,
    MAX_RETRIES
)





INTERVAL_MAP = {

    "15":

        "15min",

    "60":

        "1hour",

    "240":

        "4hour"

}







def get_kline_endpoint():

    if MARKET_TYPE == "FUTURES":

        return (

            BASE_URL

            +

            "/futures/kline"

        )


    return (

        BASE_URL

        +

        "/spot/kline"

    )








def get_market_data(
    symbol,
    timeframe="15",
    limit=200
):

    try:


        interval = INTERVAL_MAP.get(

            str(timeframe),

            "15min"

        )



        url = get_kline_endpoint()



        params = {


            "market":

            symbol,


            "period":

            interval,


            "limit":

            limit


        }




        response = None



        for attempt in range(

            MAX_RETRIES

        ):


            try:


                response = requests.get(

                    url,

                    params=params,

                    timeout=REQUEST_TIMEOUT

                )



                if response.status_code == 200:

                    break



            except Exception:


                if attempt == MAX_RETRIES - 1:

                    raise





        if not response:


            return None




        data = response.json()



        if data.get(

            "code"

        ) != 0:


            logger.error(

                data

            )


            return None






        rows = data.get(

            "data",

            []

        )



        if not rows:


            return None






        df = pd.DataFrame(

            rows

        )



        if df.empty:

            return None





        columns = [

            "time",

            "open",

            "close",

            "high",

            "low",

            "volume"

        ]



        if len(df.columns) >= 6:

            df = df.iloc[:, :6]

            df.columns = columns





        for col in [

            "open",

            "close",

            "high",

            "low",

            "volume"

        ]:


            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"

            )





        df = df.sort_values(

            "time"

        )



        df.reset_index(

            drop=True,

            inplace=True

        )





        return df





    except Exception as e:


        logger.exception(e)


        return None









def get_latest_price(
    symbol
):

    try:


        df = get_market_data(

            symbol,

            "15",

            2

        )



        if df is None or df.empty:


            return None



        return float(

            df.iloc[-1]["close"]

        )



    except Exception as e:


        logger.exception(e)


        return None









def get_multi_timeframe_data(
    symbol
):

    try:


        return {


            "15":

                get_market_data(

                    symbol,

                    "15"

                ),



            "60":

                get_market_data(

                    symbol,

                    "60"

                ),



            "240":

                get_market_data(

                    symbol,

                    "240"

                )

        }



    except Exception as e:


        logger.exception(e)


        return {}
