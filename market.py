import requests
import pandas as pd

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://api.coinex.com/v2/spot/kline"


# =========================
# HTTP Session + Retry
# =========================

session = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[
        500,
        502,
        503,
        504
    ]
)

adapter = HTTPAdapter(
    max_retries=retry
)

session.mount(
    "https://",
    adapter
)


def get_market_data(symbol, interval="15"):

    try:

        interval_map = {
            "15": "15min",
            "60": "1hour",
            "240": "4hour"
        }

        coinex_interval = interval_map.get(
            interval,
            "15min"
        )

        params = {
            "market": symbol,
            "period": coinex_interval,
            "limit": 300
        }

        response = session.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:

            raise Exception(result)

        data = result["data"]

        df = pd.DataFrame(data)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(
            columns={
                "created_at": "time",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume"
            }
        )

        required_columns = [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        if not all(
            column in df.columns
            for column in required_columns
        ):
            return pd.DataFrame()

        for column in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df.dropna(inplace=True)

        if df.empty:
            return pd.DataFrame()

        df = df.sort_values("time")

        df.reset_index(
            drop=True,
            inplace=True
        )

        return df

    except Exception as e:

        print(
            "COINEX MARKET ERROR:",
            symbol,
            interval,
            e
        )

        return pd.DataFrame()
