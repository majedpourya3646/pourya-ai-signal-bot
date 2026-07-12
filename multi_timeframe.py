from pybit.unified_trading import HTTP
import pandas as pd


session = HTTP(
    testnet=False
)



def get_market_data(symbol, interval="15"):

    try:

        response = session.get_kline(
            category="linear",
            symbol=symbol,
            interval=interval,
            limit=300
        )


        data = response["result"]["list"]


        if not data:
            raise Exception(
                "No market data"
            )


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
                "turnover"
            ]
        )



        # تبدیل نوع داده‌ها

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
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
            "MARKET ERROR:",
            symbol,
            interval,
            e
        )

        return pd.DataFrame()
