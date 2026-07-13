from core.coinex_futures import coinex

result = coinex.request(
    "GET",
    "/futures/balance"
)

print(result)
