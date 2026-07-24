# core/coin_report.py

from core.logger import logger



def create_coin_report(
    coins
):

    try:


        if not coins:


            return """

📊 <b>Coin Scanner Report</b>


❌ ارز مناسبی پیدا نشد


🤖 Pourya Trader AI

"""



        message = """

📊 <b>Coin Scanner Report</b>


"""



        for index, coin in enumerate(

            coins,

            start=1

        ):


            message += (

                f"{index}️⃣ "

                f"🪙 {coin.get('symbol')}\n"

                f"📈 تغییر: {coin.get('change',0)}٪\n"

                f"💰 حجم: {coin.get('volume',0)}\n\n"

            )



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش ارزها"
