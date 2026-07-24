# core/coin_scanner.py

from market_scanner import (
    get_all_markets
)

from core.market_filters import (
    filter_markets
)

from core.market_ranker import (
    rank_markets
)

from core.logger import logger



def scan_all_coins():

    try:


        markets = get_all_markets()



        if not markets:

            return []



        filtered = filter_markets(
            markets
        )


        ranked = rank_markets(
            filtered
        )


        return ranked



    except Exception as e:


        logger.exception(
            e
        )


        return []




def get_best_coins(
    limit=20
):

    markets = scan_all_coins()



    return markets[:limit]




def get_coin_symbols(
    limit=20
):

    coins = get_best_coins(
        limit
    )


    symbols = []



    for coin in coins:


        symbol = coin.get(
            "market"
        )


        if symbol:

            symbols.append(
                symbol
            )



    return symbols
