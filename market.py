import requests
import pandas as pd

BASE_URL = "https://api.binance.com/api/v3/klines"


def get_market_data(symbol, interval="15m", limit=200):

    response = requests.get(
        BASE_URL,
        params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(
        data,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    df[numeric_columns] = df[numeric_columns].astype(float)

    df["time"] = pd.to_datetime(df["time"], unit="ms")

    return df
