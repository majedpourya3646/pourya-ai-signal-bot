# core/coin_scanner.py

from market_scanner import (
    get_all_markets
)

from core.market_filters import (
    filter_markets
)

from core.logger import logger



def scan_market():

    try:


        markets = get_all_markets()



        if not markets:

            return []



        filtered = filter_markets(
            markets
        )



        return filtered



    except Exception as e:


        logger.exception(
            e
        )


        return []




def rank_by_volume(
    markets
):

    try:


        return sorted(

            markets,

            key=lambda x:

            float(

                x.get(
                    "volume",
                    0
                )

            ),

            reverse=True

        )



    except Exception as e:


        logger.exception(
            e
        )


        return []




def get_top_coins(
    limit=50
):

    markets = scan_market()



    ranked = rank_by_volume(
        markets
    )



    return ranked[:limit]




def get_symbols(
    limit=50
):

    coins = get_top_coins(
        limit
    )


    symbols = []



    for coin in coins:


        symbol = (

            coin.get(
                "market"
            )

            or

            coin.get(
                "symbol"
            )

        )



        if symbol:

            symbols.append(
                symbol
            )



    return symbols
