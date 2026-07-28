# core/pump_scanner_advanced.py

from market import get_market_data

from core.logger import logger






def calculate_volume_power(
    df
):

    try:


        if df is None or len(df) < 20:


            return 0





        current_volume = float(

            df["volume"].iloc[-1]

        )



        avg_volume = float(

            df["volume"].iloc[-20:-1].mean()

        )





        if avg_volume <= 0:


            return 0





        return round(

            current_volume / avg_volume,

            2

        )





    except Exception as e:


        logger.exception(e)


        return 0







def calculate_price_change(
    df
):

    try:


        if df is None or len(df) < 20:


            return 0





        old_price = float(

            df["close"].iloc[-20]

        )


        new_price = float(

            df["close"].iloc[-1]

        )





        if old_price <= 0:


            return 0





        change = (

            (

                new_price -

                old_price

            )

            /

            old_price

        ) * 100





        return round(

            change,

            2

        )





    except Exception as e:


        logger.exception(e)


        return 0







def detect_advanced_pump(
    symbol
):

    try:



        df = get_market_data(

            symbol,

            interval="15"

        )





        if df is None or df.empty:


            return None






        change = calculate_price_change(

            df

        )



        volume_power = calculate_volume_power(

            df

        )





        score = 0



        reasons = []





        if change >= 2:



            score += 35


            reasons.append(

                "PRICE MOMENTUM"

            )






        if volume_power >= 2:



            score += 40


            reasons.append(

                "VOLUME SPIKE"

            )






        if change > 0:



            score += 15


            reasons.append(

                "POSITIVE MOVE"

            )






        if volume_power >= 1.5 and change >= 1:



            score += 10


            reasons.append(

                "EARLY PUMP"

            )






        if score < 60:


            return None





        signal = "BUY"





        return {



            "symbol":

            symbol,



            "signal":

            signal,



            "confidence":

            score,



            "score":

            score,



            "entry":

            float(

                df["close"].iloc[-1]

            ),



            "price":

            float(

                df["close"].iloc[-1]

            ),



            "change":

            change,



            "volume_power":

            volume_power,



            "reasons":

            reasons



        }





    except Exception as e:


        logger.exception(e)


        return None







def scan_advanced_pumps(
    symbols
):

    results = []



    try:



        if not symbols:


            return []





        for symbol in symbols:



            result = detect_advanced_pump(

                symbol

            )



            if result:


                results.append(

                    result

                )






        results.sort(

            key=lambda x:

            x.get(

                "score",

                0

            ),

            reverse=True

        )





        logger.info(

            f"ADVANCED PUMPS FOUND: {len(results)}"

        )



        return results





    except Exception as e:


        logger.exception(e)


        return []
