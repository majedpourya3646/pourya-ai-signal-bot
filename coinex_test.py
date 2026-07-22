from coinex_api import coinex


def main():

    print("=" * 60)
    print("COINEX PRIVATE API TEST")
    print("=" * 60)

    print("\n1) Testing Futures Balance...\n")

    balance = coinex.get_balance()

    if balance is None:
        print("❌ No response from CoinEx")
        return

    print(balance)

    print("\n" + "=" * 60)

    if balance.get("code") == 0:

        print("✅ CoinEx Private API Connected")

        print("\nMessage:")
        print(balance.get("message"))

        print("\nData:")
        print(balance.get("data"))

    else:

        print("❌ CoinEx API Error")

        print("Code:", balance.get("code"))
        print("Message:", balance.get("message"))


if __name__ == "__main__":
    main()
