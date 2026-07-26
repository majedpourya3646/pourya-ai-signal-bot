# core/coin_scanner.py

from core.market_discovery import (
    discover_markets
)

from core.market_filters import (
    filter_market
)

from core.logger import logger





def get_symbols():

    try:

        markets = discover_markets()



        if not markets:

            logger.warning(
                "NO MARKET DATA RECEIVED"
            )

            return []



        logger.info(
            f"RAW MARKETS COUNT: {len(markets)}"
        )



        if len(markets) > 0:

            logger.info(
                f"RAW MARKET SAMPLE: {markets[0]}"
            )



        filtered = filter_market(
            markets
        )

        filtered = rank_by_volume(filtered)

        symbols = []



        for item in filtered:


            symbol = item.get(
                "symbol"
            )


            if symbol:

                symbols.append(
                    symbol
                )



        logger.info(

            f"AVAILABLE SYMBOLS: {len(symbols)}"

        )



        return symbols



    except Exception as e:

        logger.exception(e)

        return []





def rank_by_volume(
    markets
):

    try:

        if not markets:

            return []



        if not isinstance(
            markets,
            list
        ):

            return []



        return sorted(

            markets,

            key=lambda x:

                float(

                    x.get(
                        "volume",
                        0
                    )

                    or 0

                ),

            reverse=True

        )



    except Exception as e:

        logger.exception(e)

        return []
