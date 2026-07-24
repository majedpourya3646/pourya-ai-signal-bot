# core/pump_report.py

from core.logger import logger



def create_pump_report(
    pumps
):

    try:


        if not pumps:


            return """

🚀 <b>PUMP SCANNER</b>


❌ هیچ پامپی پیدا نشد


🤖 Pourya Trader AI

"""



        message = """

🚀 <b>PUMP ALERT</b>


"""



        for index, item in enumerate(

            pumps,

            start=1

        ):



            message += (

                f"{index}️⃣ "

                f"🪙 {item.get('symbol')}\n"

                f"⭐ قدرت: {item.get('score')}٪\n"

                f"📈 تغییر: {item.get('change')}٪\n"

                f"🔥 حجم: x{item.get('volume_power')}\n\n"

            )



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در ساخت گزارش پامپ"
