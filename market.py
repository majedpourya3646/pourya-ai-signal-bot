from pybit.unified_trading import HTTP
import pandas as pd


session = HTTP(
    testnet=False
)


def get_market_data(symbol, interval="15"):

    try:

        result = session.get_kline(
            category="linear",
            symbol=symbol,
            interval=interval,
            limit=300
        )


        rows = result["result"]["list"]


        if not rows:
            print("NO DATA:", symbol, interval)
            return pd.DataFrame()



        rows.reverse()



        df = pd.DataFrame(rows)



        # نام‌گذاری بر اساس پاسخ بای‌بیت
        df.columns = [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
        ]



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
