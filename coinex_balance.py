from coinex_api import coinex


def get_futures_balance():

    result = coinex.get_futures_balance()

    if not result:
        return None

    if result.get("code") != 0:
        print("CoinEx Error:")
        print(result)
        return None

    return result.get("data")



if __name__ == "__main__":

    print("=" * 50)
    print("COINEX FUTURES BALANCE")
    print("=" * 50)

    balance = get_futures_balance()

    print(balance)
