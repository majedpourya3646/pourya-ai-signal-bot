# core/market_filters.py

from core.logger import logger





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



            symbol = market.get(
                "market",
                ""
            )



            volume = float(
                market.get(
                    "volume",
                    0
                )
                or 0
            )



            last = float(
                market.get(
                    "last",
                    0
                )
                or 0
            )



            if not symbol:

                continue



            if not symbol.endswith(
                "USDT"
            ):

                continue



            if volume <= 0:

                continue



            if last <= 0:

                continue



            filtered.append(

                {

                    "symbol": symbol,

                    "volume": volume,

                    "last": last

                }

            )



        logger.info(

            f"FILTERED MARKETS: {len(filtered)}"

        )



        return filtered



    except Exception as e:

        logger.exception(e)

        return []
