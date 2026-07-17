from coinex_api import coinex


print("=" * 50)
print("COINEX BALANCE TEST")
print("=" * 50)


print("\nFUTURES BALANCE")
print("----------------")

futures = coinex.get_futures_balance()

print(futures)



print("\nSPOT BALANCE")
print("----------------")

spot = coinex.get_spot_balance()

print(spot)
