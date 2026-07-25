# core/scanner_service.py

from core.coin_scanner import (
    get_symbols
)

from core.opportunity_engine import (
    find_opportunities
)

from core.market_filters import (
    filter_symbols
)

from core.logger import logger



def run_scanner():

    try:

        symbols = get_symbols()


        if not symbols:

            return []



        symbols = filter_symbols(
            symbols
        )


        opportunities = find_opportunities(
            len(symbols)
        )


        return opportunities



    except Exception as e:

        logger.exception(e)

        return []





def scan_symbol(
    symbol
):

    try:

        opportunities = find_opportunities(
            1
        )


        for item in opportunities:

            if item.get(
                "symbol"
            ) == symbol:

                return item



        return None



    except Exception as e:

        logger.exception(e)

        return None
