# core/market_discovery.py

from core.coin_scanner import (
    scan_all_coins
)

from core.logger import logger



def discover_markets():

    try:


        markets = scan_all_coins()



        discovered = []



        for market in markets:


            symbol = (

                market.get(
                    "market"
                )

                or

                market.get(
                    "symbol"
                )

            )



            if not symbol:

                continue



            discovered.append(

                {

                    "symbol": symbol,

                    "score": market.get(
                        "score",
                        0
                    ),

                    "change": market.get(
                        "change",
                        0
                    ),

                    "volume": market.get(
                        "volume",
                        0
                    )

                }

            )



        return discovered



    except Exception as e:


        logger.exception(
            e
        )


        return []




def get_new_symbols(
    limit=50
):

    markets = discover_markets()



    markets.sort(

        key=lambda x: x.get(
            "score",
            0
        ),

        reverse=True

    )



    return [

        item["symbol"]

        for item in markets[:limit]

    ]
