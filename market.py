import requests
import pandas as pd


def get_market_data(symbol="BTCUSDT", interval="15m", limit=100):

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)

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
            "ignore"
        ]
    )

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["open"] = df["open"].astype(float)
df["high"] = df["high"].astype(float)
df["low"] = df["low"].astype(float)
    return df
