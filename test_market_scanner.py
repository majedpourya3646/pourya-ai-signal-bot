# test_market_scanner.py

from market_scanner import (
    scan_market,
    get_top_symbols
)


print(
    "START MARKET SCANNER TEST"
)


markets = scan_market()


print(
    "\nTOP MARKETS:"
)


for item in markets:

    print(
        item
    )



print(
    "\nTOP SYMBOLS:"
)


symbols = get_top_symbols()


for symbol in symbols:

    print(
        symbol
    )


print(
    "\nTEST FINISHED"
)
