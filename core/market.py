# core/market.py

import pandas as pd

from core.logger import logger

from core.mt5_connector import (
    get_rates
)



TIMEFRAME_MAP = {

    "1": "1",

    "5": "5",

    "15": "15",

    "30": "30",

    "60": "60",

    "240": "240",

    "1440": "1440"

}





def get_market_data(
    symbol,
    timeframe="15",
    count=200
):

    try:

        logger.info(
            f"MARKET DATA {symbol} TF={timeframe} COUNT={count}"
        )


        rates = get_rates(
            symbol,
            timeframe,
            count
        )


        if rates is None:

            logger.error(
                f"NO MARKET DATA {symbol}"
            )

            return None



        df = pd.DataFrame(
            rates
        )



        df["time"] = pd.to_datetime(
            df["time"],
            unit="s"
        )



        df.rename(
            columns={

                "open": "open",

                "high": "high",

                "low": "low",

                "close": "close",

                "tick_volume": "volume"

            },
            inplace=True
        )



        df = df[

            [

                "time",

                "open",

                "high",

                "low",

                "close",

                "volume"

            ]

        ]



        return df



    except Exception as e:


        logger.error(
            f"MARKET DATA ERROR {e}"
        )


        return None





def get_current_price(
    symbol
):

    try:

        df = get_market_data(
            symbol,
            "15",
            2
        )


        if df is None:

            return None



        price = float(
            df.iloc[-1]["close"]
        )


        return price



    except Exception as e:


        logger.error(
            f"CURRENT PRICE ERROR {e}"
        )


        return None
