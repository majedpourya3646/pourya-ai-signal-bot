# core/engine_report.py

from core.logger import logger



def create_engine_report(
    trades
):

    try:


        if not trades:


            return """

⚙️ <b>TRADING ENGINE</b>


⏳ امروز معامله‌ای اجرا نشد


🤖 Pourya Trader AI

"""



        message = """

⚙️ <b>AUTO TRADING ENGINE</b>


"""



        for index, trade in enumerate(

            trades,

            start=1

        ):


            message += (

                f"{index}️⃣\n"

                f"🪙 ارز: {trade.get('symbol')}\n"

                f"✅ سفارش اجرا شد\n\n"

            )



        message += (

            "🤖 Pourya Trader AI"

        )


        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در ساخت Engine Report"
