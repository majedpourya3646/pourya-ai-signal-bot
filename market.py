import requests
import pandas as pd


BASE_URL = "https://api.binance.com/api/v3/klines"



def get_market_data(symbol, interval="15"):

    try:

        interval_map = {
            "15": "15m",
            "60": "1h",
            "240": "4h"
        }


        binance_interval = interval_map.get(
            interval,
            interval
        )


        params = {
            "symbol": symbol,
            "interval": binance_interval,
            "limit": 300
        }


        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )


        data = response.json()



        if "code" in data:

            raise Exception(
                data.get("msg")
            )



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



        df.dropna(
            inplace=True
        )



        return df



    except Exception as e:

        print(
            "BINANCE MARKET ERROR:",
            symbol,
            interval,
            e
        )

        return pd.DataFrame()
