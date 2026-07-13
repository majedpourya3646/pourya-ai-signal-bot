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

        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:
            logger.error(result)
            return pd.DataFrame()

        df = pd.DataFrame(result["data"])

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns={
            "created_at": "time"
        })

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:
            df[col] = pd.to_numeric(
                df[col],
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
