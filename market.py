import pandas as pd

from config import BASE_URL
from core.session import session
from core.logger import logger


KLINE_URL = BASE_URL + "/spot/kline"


INTERVAL_MAP = {
    "15": "15min",
    "60": "1hour",
    "240": "4hour"
}


def get_market_data(symbol, interval="15"):

    try:

        params = {
            "market": symbol,
            "period": INTERVAL_MAP.get(interval, "15min"),
            "limit": 300
        }

        response = session.get(
            KLINE_URL,
            params=params,
            timeout=session.request_timeout
        )

        print("==========================")
        print("MARKET URL:", response.url)
        print("STATUS:", response.status_code)
        print("BODY:")
        print(response.text)
        print("==========================")

        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:
            logger.error(result)
            return pd.DataFrame()

        data = result.get("data", [])

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

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
            df["time"] = range(len(df))

        for column in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        df.dropna(inplace=True)

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

        logger.exception(e)

        return pd.DataFrame()
