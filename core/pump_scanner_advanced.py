# core/pump_scanner_advanced.py

from market import get_market_data

from core.logger import logger



def calculate_volume_power(
    df
):

    try:


        if len(df) < 20:

            return 0



        current_volume = float(

            df["volume"].iloc[-1]

        )


        avg_volume = float(

            df["volume"].iloc[-20:-1].mean()

        )



        if avg_volume == 0:

            return 0



        return round(

            current_volume / avg_volume,

            2

        )



    except Exception as e:


        logger.exception(
            e
        )


        return 0




def calculate_price_change(
    df
):

    try:


        old_price = float(

            df["close"].iloc[-20]

        )


        new_price = float(

            df["close"].iloc[-1]

        )



        if old_price == 0:

            return 0



        return round(

            (

                (

                    new_price - old_price

                )

                /

                old_price

            )

            *

            100,

            2

        )



    except Exception as e:


        logger.exception(
            e
        )


        return 0




def detect_advanced_pump(
    symbol
):

    try:


        df = get_market_data(

            symbol,

            interval="15"

        )



        if df.empty:

            return None



        change = calculate_price_change(
            df
        )


        volume_power = calculate_volume_power(
            df
        )



        score = 0



        if change >= 2:

            score += 40



        if volume_power >= 2:

            score += 40



        if change > 0:

            score += 20



        if score < 60:

            return None



        return {

            "symbol": symbol,

            "score": score,

            "change": change,

            "volume_power": volume_power

        }



    except Exception as e:


        logger.exception(
            e
        )


        return None




def scan_advanced_pumps(
    symbols
):

    results = []



    for symbol in symbols:


        result = detect_advanced_pump(
            symbol
        )



        if result:


            results.append(
                result
            )



    results.sort(

        key=lambda x: x.get(
            "score",
            0
        ),

        reverse=True

    )



    return results
