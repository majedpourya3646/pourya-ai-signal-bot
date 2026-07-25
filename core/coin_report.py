# core/coin_report.py

from core.logger import logger



def create_coin_report(
    coins
):

    try:

        if not coins:

            return (
                "🪙 COIN REPORT\n\n"
                "No coin data available."
            )



        report = (

            "🪙 POURYA TRADER AI COIN REPORT\n\n"

        )



        for coin in coins:


            symbol = coin.get(
                "symbol",
                "UNKNOWN"
            )


            price = coin.get(
                "price",
                0
            )


            change = coin.get(
                "change",
                0
            )


            volume = coin.get(
                "volume",
                0
            )



            report += (

                f"🔹 {symbol}\n"

                f"💰 Price: {price}\n"

                f"📈 Change: {change}%\n"

                f"📊 Volume: {volume}\n\n"

            )



        return report



    except Exception as e:

        logger.exception(e)

        return "Coin report error."
