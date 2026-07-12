import requests
import pandas as pd


def get_market_data(symbol, interval="15"):

    url = "https://api.coinex.com/v2/spot/kline"

    params = {
        "market": symbol.lower(),
        "period": interval,
        "limit": 300
    }

    response = requests.get(url, params=params)

    result = response.json()

    data = result["data"]

    df = pd.DataFrame(data)

    df = df.rename(columns={
        "created_at": "time",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume"
    })

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df
