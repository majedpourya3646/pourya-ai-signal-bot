import pandas as pd

from config import (
    BASE_URL,
    MARKET_TYPE
)

from core.session import session
from core.logger import logger



if MARKET_TYPE == "FUTURES":
    KLINE_URL = BASE_URL + "/futures/kline"
else:
    KLINE_URL = BASE_URL + "/spot/kline"



INTERVAL_MAP = {
    "15": "15min",
    "60": "1hour",
    "240": "4hour"
}



def get_market_data(
    symbol,
    interval="15"
):

    try:

        params = {
            "market": symbol,
            "period": INTERVAL_MAP.get(
                interval,
                "15min"
            ),
            "limit": 300
        }


        response = session.get(
            KLINE_URL,
            params=params
        )


        logger.info(
            f"KLINE URL: {response.url}"
        )

        logger.info(
            f"STATUS: {response.status_code}"
        )


        response.raise_for_status()


        result = response.json()


        if result.get("code") != 0:

            logger.error(
                result
            )

            return pd.DataFrame()



        data = result.get(
            "data",
            []
        )


        if not data:

            return pd.DataFrame()



        df = pd.DataFrame(
            data
        )



        # CoinEx V2 format
        if "created_at" in df.columns:

            df.rename(
                columns={
                    "created_at": "time"
                },
                inplace=True
            )


        elif "timestamp" in df.columns:

            df.rename(
                columns={
                    "timestamp": "time"
                },
                inplace=True
            )


        elif "time" not in df.columns:

            df["time"] = range(
                len(df)
            )



        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]


        for col in numeric_columns:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )


        df.dropna(
            inplace=True
        )


        df.sort_values(
            "time",
            inplace=True
        )


        df.reset_index(
            drop=True,
            inplace=True
        )


        return df



    except Exception as e:

        logger.exception(
            e
        )

        return pd.DataFrame()
