# core/scanner_service.py

from market_scanner import scan_market

from core.market_ranker import rank_markets

from core.market_cache import (
    save_cache,
    load_cache
)

from core.logger import logger



def get_market_opportunities(
    force_refresh=False
):

    try:


        if not force_refresh:


            cached = load_cache()



            if cached:


                return cached



        markets = scan_market()



        if not markets:


            return []



        ranked = rank_markets(
            markets
        )



        save_cache(
            ranked
        )


        return ranked



    except Exception as e:


        logger.exception(
            e
        )


        return []




def get_top_opportunities(
    limit=10
):

    markets = get_market_opportunities()



    return markets[:limit]




def get_symbols(
    limit=10
):

    markets = get_top_opportunities(
        limit
    )


    symbols = []



    for item in markets:


        symbol = item.get(
            "symbol"
        )


        if symbol:

            symbols.append(
                symbol
            )



    return symbols
