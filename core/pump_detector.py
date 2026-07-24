# core/pump_detector.py

from core.logger import logger

from market import get_market_data



MIN_VOLUME_POWER = 3
MIN_PRICE_CHANGE = 5
MAX_RESULTS = 10



def calculate_volume_power(df):

    try:

        if len(df) < 20:

            return 0



        average_volume = (

            df["volume"]

            .rolling(20)

            .mean()

            .iloc[-1]

        )


        current_volume = (

            df["volume"]

            .iloc[-1]

        )



        if average_volume == 0:

            return 0



        return round(

            current_volume / average_volume,

            2

        )



    except Exception as e:


        logger.exception(
            e
        )


        return 0




def calculate_change(df):

    try:


        previous = float(

            df["close"]

            .iloc[-2]

        )


        current = float(

            df["close"]

            .iloc[-1]

        )


        return round(

            (

                (current - previous)

                /

                previous

            ) * 100,

            2

        )



    except Exception:


        return 0




def calculate_score(
    volume_power,
    change
):


    score = 0



    if volume_power >= 5:

        score += 50


    elif volume_power >= 3:

        score += 35



    if change >= 10:

        score += 40


    elif change >= 5:

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



        volume_power = calculate_volume_power(
            df
        )


        change = calculate_change(
            df
        )



        score = calculate_score(

            volume_power,

            change

        )



        if (

            volume_power >= MIN_VOLUME_POWER

            and

            change >= MIN_PRICE_CHANGE

        ):


            return {

                "symbol": symbol,

                "score": score,

                "volume_power": volume_power,

                "change": change

            }



        return None



    except Exception as e:


        logger.exception(
            e
        )


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



    return results[:MAX_RESULTS]
