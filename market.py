from pybit.unified_trading import HTTP
import pandas as pd

session = HTTP(testnet=False)


def get_market_data(symbol, interval="15"):

    kline = session.get_kline(
        category="linear",
        symbol=symbol,
        interval=interval,
        limit=300,
    )

    data = kline["result"]["list"]

    data.reverse()

    df = pd.DataFrame(
        data,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
        ],
    )

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df
