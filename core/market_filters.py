# core/market_filters.py

from core.logger import logger



MIN_VOLUME = 100000

MIN_PRICE_CHANGE = -10

MAX_PRICE_CHANGE = 20



def filter_markets(
    markets
):

    try:


        result = []



        for market in markets:


            try:


                volume = float(

                    market.get(
                        "volume",
                        0
                    )

                )


                change = float(

                    market.get(
                        "change",
                        0
                    )

                )



                if volume < MIN_VOLUME:

                    continue



                if change < MIN_PRICE_CHANGE:

                    continue



                if change > MAX_PRICE_CHANGE:

                    continue



                result.append(

                    {

                        "symbol": market.get(
                            "market"
                        ),

                        "volume": volume,

                        "change": change

                    }

                )



            except Exception:


                continue



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return []
