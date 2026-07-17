from coinex_api import coinex


print("=" * 60)
print("        COINEX BALANCE TEST")
print("=" * 60)



print("\n1) FUTURES BALANCE")
print("-" * 60)

futures = coinex.get_futures_balance()

print(futures)



print("\n2) SPOT BALANCE")
print("-" * 60)

spot = coinex.get_spot_balance()

print(spot)



print("\n" + "=" * 60)


if futures and futures.get("code") == 0:
    print("✅ Futures API Connected")
else:
    print("❌ Futures API Failed")



if spot and spot.get("code") == 0:
    print("✅ Spot API Connected")
else:
    print("❌ Spot API Failed")


print("=" * 60)
