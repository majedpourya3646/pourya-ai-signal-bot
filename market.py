import requests
import pandas as pd


BASE_URL = "https://api.coinex.com/v2/spot/kline"



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


        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )


        result = response.json()


        if result.get("code") != 0:

            raise Exception(
                result
            )


        data = result["data"]



        df = pd.DataFrame(
            data
        )



        # هماهنگ سازی نام ستون‌ها

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



        df = df.sort_values(
            "time"
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
