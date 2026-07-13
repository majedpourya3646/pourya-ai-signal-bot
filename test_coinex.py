from coinex_futures_api import coinex


def main():

    print("================================")
    print("   COINEX FUTURES TEST")
    print("================================")

    print("\n1) Checking Futures Balance...\n")

    try:
        balance = coinex.get_futures_balance()

        print("BALANCE RESULT:")
        print(balance)

    except Exception as e:
        print("BALANCE ERROR:")
        print(e)


    print("\n--------------------------------")


    print("\n2) Checking Futures Positions...\n")

    try:
        positions = coinex.get_futures_positions()

        print("POSITIONS RESULT:")
        print(positions)

    except Exception as e:
        print("POSITIONS ERROR:")
        print(e)



if __name__ == "__main__":
    main()
