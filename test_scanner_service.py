# test_scanner_service.py

from core.scanner_service import (
    get_market_opportunities,
    get_top_opportunities,
    get_symbols
)



print(
    "START SCANNER SERVICE TEST"
)



markets = get_market_opportunities(
    force_refresh=True
)



print(
    "\nALL RESULTS:"
)



for item in markets[:10]:

    print(
        item
    )



print(
    "\nTOP SYMBOLS:"
)



symbols = get_symbols(
    limit=10
)



for symbol in symbols:

    print(
        symbol
    )



print(
    "\nTEST FINISHED"
)
