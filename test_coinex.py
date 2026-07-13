from coinex_futures_api import coinex

print("===== COINEX FUTURES TEST =====")

balance = coinex.get_futures_balance()

print(balance)
