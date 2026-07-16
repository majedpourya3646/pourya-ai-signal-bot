from coinex_api import coinex


print("=" * 50)
print("Testing CoinEx API...")
print("=" * 50)


result = coinex.get_balance()


if result:

    print("✅ اتصال موفق به CoinEx")

    print(result)


else:

    print("❌ اتصال ناموفق")
    print("API Key یا Signature یا Endpoint بررسی شود")
