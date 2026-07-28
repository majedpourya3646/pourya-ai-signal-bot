# core/market_filters.py

from core.logger import logger





MIN_VOLUME = 0

MIN_PRICE = 0





def normalize_symbol(
    symbol
):

    try:


        if not symbol:


            return None



        return str(

            symbol

        ).upper().replace(

            "-",

            ""

        ).replace(

            "_",

            ""

        )



    except Exception:


        return None






def filter_market(
    markets
):

    try:



        filtered = []





        if not isinstance(

            markets,

            list

        ):



            logger.error(

                "MARKET FILTER INPUT IS NOT LIST"

            )


            return []







        for market in markets:



            if not isinstance(

                market,

                dict

            ):


                continue






            symbol = normalize_symbol(

                market.get(

                    "symbol",

                    market.get(

                        "market",

                        ""

                    )

                )

            )





            if not symbol:


                continue






            volume = float(

                market.get(

                    "volume",

                    market.get(

                        "turnover",

                        0

                    )

                )

                or 0

            )





            price = float(

                market.get(

                    "price",

                    market.get(

                        "last",

                        market.get(

                            "close",

                            0

                        )

                    )

                )

                or 0

            )







            if not symbol.endswith(

                "USDT"

            ):


                continue





            if volume <= MIN_VOLUME:


                continue





            if price <= MIN_PRICE:


                continue





            filtered.append(

                {

                    "symbol":

                    symbol,


                    "volume":

                    volume,


                    "price":

                    price,


                    "last":

                    price

                }

            )







        logger.info(

            f"FILTERED MARKETS: {len(filtered)}"

        )





        return filtered





    except Exception as e:



        logger.exception(e)


        return []
