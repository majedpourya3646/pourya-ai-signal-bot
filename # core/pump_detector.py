import pandas as pd

from core.logger import logger
from market import get_market_data


VOLUME_MULTIPLIER = 3
MIN_CHANGE_PERCENT = 5
MAX_RSI = 75


def calculate_volume_strength(df):

    try:

        if len(df) < 30:
            return 0


        avg_volume = (
            df["volume"]
            .rolling(20)
            .mean()
            .iloc[-1]
        )


        current_volume = (
            df["volume"]
            .iloc[-1]
        )


        if avg_volume == 0:

            return 0


        return round(
            current_volume / avg_volume,
            2
        )


    except Exception as e:

        logger.exception(e)

        return 0



def calculate_price_change(df):

    try:

        old_price = float(
            df["close"].iloc[-2]
        )

        current_price = float(
            df["close"].iloc[-1]
        )


        change = (
            (current_price - old_price)
            /
            old_price
        ) * 100


        return round(
            change,
            2
        )


    except Exception:

        return 0



def calculate_pump_score(
    volume_power,
    price_change
):

    score = 0


    if volume_power >= 3:

        score += 40


    elif volume_power >= 2:

        score += 25



    if price_change >= 10:

        score += 40


    elif price_change >= 5:

        score += 25



    if score > 100:

        score = 100


    return score



def detect_pump(symbol):

    try:

        df = get_market_data(
            symbol,
            interval="15"
        )


        if df.empty:

            return None



        volume_power = calculate_volume_strength(
            df
        )


        price_change = calculate_price_change(
            df
        )



        score = calculate_pump_score(
            volume_power,
            price_change
        )



        if (

            volume_power >= VOLUME_MULTIPLIER

            and

            price_change >= MIN_CHANGE_PERCENT

        ):


            return {

                "symbol": symbol,

                "score": score,

                "volume_power": volume_power,

                "change": price_change,

                "status": "PUMP"

            }



        return None



    except Exception as e:

        logger.exception(e)

        return None



def scan_pumps(symbols):

    results = []


    for symbol in symbols:


        result = detect_pump(
            symbol
        )


        if result:

            results.append(
                result
            )



    results.sort(

        key=lambda x: x["score"],

        reverse=True

    )


    return results



if __name__ == "__main__":


    test_symbols = [

        "BTCUSDT",

        "ETHUSDT",

        "SOLUSDT"

    ]


    print(
        scan_pumps(test_symbols)
    )
