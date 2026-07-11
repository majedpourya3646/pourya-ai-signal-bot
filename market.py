import requests
import pandas as pd


def get_market_data(symbol="BTCUSDT", interval="15min", limit=100):

    url = "https://api.coinex.com/v2/spot/kline"

    params = {
        "market": symbol,
        "period": interval,
        "limit": limit
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()["data"]

    df = pd.DataFrame(
        data,
        columns=[
            "time",
            "open",
            "close",
            "high",
            "low",
            "volume",
            "amount"
        ]
    )

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df
