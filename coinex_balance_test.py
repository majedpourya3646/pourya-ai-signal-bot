from coinex_api import coinex


print("=" * 50)
print("COINEX BALANCE TEST")
print("=" * 50)


balance = coinex.get_futures_balance()


print(balance)
