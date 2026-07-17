from coinex_api import coinex
from core.logger import logger


def main():

    print("=" * 60)
    print("COINEX PRIVATE API TEST")
    print("=" * 60)


    print("\n1) Testing Futures Balance...\n")

    balance = coinex.get_futures_balance()


    if balance is None:
        print("❌ No response from CoinEx")
        return


    print(balance)


    print("\n" + "=" * 60)


    if balance.get("code") == 0:

        print("✅ CoinEx Private API Connected")

        data = balance.get("data")

        print("\nBalance Data:")
        print(data)


    else:

        print("❌ CoinEx API Error")

        print(
            "Code:",
            balance.get("code")
        )

        print(
            "Message:",
            balance.get("message")
        )


if __name__ == "__main__":
    main()
