# core/coin_report.py

from core.logger import logger



def create_coin_report(
    coins
):

    try:


        if not coins:


            return """

🪙 <b>COIN SCANNER</b>


❌ ارز مناسبی پیدا نشد


🤖 Pourya Trader AI

"""



        message = """

🪙 <b>TOP COINS SCANNER</b>


"""



        for index, coin in enumerate(

            coins,

            start=1

        ):


            message += (

                f"{index}️⃣ "

                f"🪙 {coin.get('market')}\n"

                f"⭐ امتیاز: {coin.get('score')}٪\n"

                f"📈 تغییر: {coin.get('change')}٪\n"

                f"📊 حجم: {coin.get('volume')}\n\n"

            )



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در ساخت Coin Report"
