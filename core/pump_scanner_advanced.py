# core/pump_scanner_advanced.py

from core.logger import logger

from core.market import (
    get_market_data
)

from config import (
    SYMBOLS
)








def calculate_pump_score(
    candles
):

    try:


        if len(candles) < 20:

            return 0





        current = candles[-1]

        previous = candles[-10]





        price_change = (

            (

                current["close"]

                -

                previous["close"]

            )

            /

            previous["close"]

        ) * 100






        volumes = [

            x["volume"]

            for x in candles[-20:]

        ]



        avg_volume = sum(

            volumes

        ) / len(

            volumes

        )



        volume_score = 0





        if current["volume"] > avg_volume * 2:


            volume_score = 40



        elif current["volume"] > avg_volume * 1.5:


            volume_score = 25







        price_score = 0



        if abs(price_change) >= 5:


            price_score = 40



        elif abs(price_change) >= 3:


            price_score = 25







        momentum_score = 20





        return min(

            price_score

            +

            volume_score

            +

            momentum_score,

            100

        )



    except Exception as e:


        logger.exception(e)


        return 0







def scan_advanced_pumps():

    try:


        results = []





        for symbol in SYMBOLS:



            candles = get_market_data(

                symbol,

                "15"

            )



            if not candles:


                continue





            score = calculate_pump_score(

                candles

            )





            if score >= 50:



                results.append(

                    {


                        "symbol":

                            symbol,



                        "pump_score":

                            score,



                        "price":

                            candles[-1]["close"]

                    }

                )







        results.sort(

            key=lambda x:

            x["pump_score"],

            reverse=True

        )





        return results



    except Exception as e:


        logger.exception(e)


        return []
