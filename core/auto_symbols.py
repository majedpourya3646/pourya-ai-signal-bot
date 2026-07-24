# core/auto_symbols.py

from core.coin_scanner import (
    get_coin_symbols
)

from config import (
    SYMBOLS
)

from core.logger import logger



def update_symbols(
    limit=20
):

    try:


        new_symbols = get_coin_symbols(
            limit
        )


        if not new_symbols:

            return SYMBOLS



        for symbol in new_symbols:


            if symbol not in SYMBOLS:


                SYMBOLS.append(
                    symbol
                )



        return SYMBOLS



    except Exception as e:


        logger.exception(
            e
        )


        return SYMBOLS
