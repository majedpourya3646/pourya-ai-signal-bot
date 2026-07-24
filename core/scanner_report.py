# core/scanner_report.py

from core.logger import logger



def create_scanner_report(markets):

    try:

        if not markets:

            return (
                "🔎 <b>Market Scanner</b>\n\n"
                "❌ فرصت مناسبی پیدا نشد"
            )


        text = """

🔎 <b>Market Scanner</b>


"""


        for index, item in enumerate(

            markets[:10],

            start=1

        ):


            text += (

                f"{index}️⃣ "

                f"🪙 {item.get('symbol')}\n"

                f"⭐ امتیاز: {item.get('score')}٪\n"

                f"📈 تغییر: {item.get('change')}٪\n"

                f"📊 حجم: {item.get('volume')}\n\n"

            )


        text += (

            "🤖 Pourya Trader AI"

        )


        return text



    except Exception as e:


        logger.exception(
            e
        )


        return (

            "❌ خطا در ساخت گزارش Scanner"

        )
