# test_coin_scanner.py

from core.coin_scanner import (
    scan_all_coins,
    get_best_coins,
    get_coin_symbols
)

from core.coin_report import (
    create_coin_report
)



print(
    "START COIN SCANNER TEST"
)



try:


    coins = scan_all_coins()



    print(
        "\nALL COINS:"
    )



    for coin in coins[:20]:

        print(
            coin
        )



    print(
        "\nBEST COINS:"
    )



    best = get_best_coins(
        10
    )



    report = create_coin_report(
        best
    )



    print(
        report
    )



    print(
        "\nSYMBOLS:"
    )



    symbols = get_coin_symbols(
        10
    )



    for symbol in symbols:

        print(
            symbol
        )



except Exception as e:


    print(
        "ERROR:",
        e
    )



print(
    "COIN SCANNER TEST FINISHED"
)
