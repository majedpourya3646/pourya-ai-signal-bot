# core/coin_scanner.py

from core.market_discovery import (
    discover_markets
)

from core.market_filters import (
    filter_market
)

from core.logger import (
    logger
)





ALLOWED_SYMBOLS = {

    "BTCUSDT",

    "ETHUSDT",

    "BNBUSDT",

    "SOLUSDT",

    "XRPUSDT",

    "DOGEUSDT",

    "ADAUSDT",

    "TRXUSDT",

    "LINKUSDT",

    "AVAXUSDT",

    "DOTUSDT",

    "LTCUSDT",

    "BCHUSDT",

    "ATOMUSDT",

    "UNIUSDT",

    "APTUSDT",

    "ARBUSDT",

    "OPUSDT",

    "NEARUSDT",

    "FILUSDT",

    "SUIUSDT",

    "SEIUSDT",

    "INJUSDT",

    "FETUSDT",

    "AAVEUSDT",

    "TIAUSDT",

    "WLDUSDT",

    "TONUSDT",

    "PEPEUSDT",

    "SHIBUSDT",

    "BONKUSDT",

    "FLOKIUSDT",

    "JUPUSDT",

    "ENAUSDT",

    "RENDERUSDT",

    "ONDOUSDT",

    "TAOUSDT",

    "ICPUSDT",

    "ETCUSDT",

    "EOSUSDT"

}







def rank_markets(
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

                or 0

            ),

            reverse=True

        )



    except Exception as e:


        logger.exception(e)


        return []








def normalize_symbol(
    symbol
):

    try:


        if not symbol:


            return None



        symbol = str(

            symbol

        ).upper().replace(

            "-",

            ""

        ).replace(

            "_",

            ""

        )



        return symbol



    except Exception:


        return None








def get_symbols():

    try:



        markets = discover_markets()



        if not markets:


            logger.info(

                "NO MARKETS DISCOVERED"

            )


            return []





        markets = filter_market(

            markets

        )





        if not markets:


            return []





        markets = rank_markets(

            markets

        )





        symbols = []





        for item in markets:



            symbol = normalize_symbol(

                item.get(

                    "symbol"

                )

            )



            if not symbol:


                continue




            if symbol in ALLOWED_SYMBOLS:



                symbols.append(

                    symbol

                )





        # حذف تکراری‌ها

        symbols = list(

            dict.fromkeys(

                symbols

            )

        )





        logger.info(

            f"VALID FUTURES SYMBOLS: {len(symbols)}"

        )



        logger.info(

            symbols

        )





        return symbols





    except Exception as e:


        logger.exception(e)


        return []
