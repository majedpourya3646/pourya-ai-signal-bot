# core/opportunity_report.py

from core.logger import logger



def create_opportunity_report(
    opportunities
):

    try:


        if not opportunities:


            return """

🎯 <b>OPPORTUNITY SCANNER</b>


❌ فرصت معاملاتی قوی پیدا نشد


🤖 Pourya Trader AI

"""



        message = """

🎯 <b>OPPORTUNITY ALERT</b>


"""



        for index, item in enumerate(

            opportunities,

            start=1

        ):


            message += (

                f"{index}️⃣ "

                f"🪙 {item.get('symbol')}\n"

                f"🚦 وضعیت: {item.get('signal')}\n"

                f"⭐ قدرت: {item.get('confidence')}٪\n"

                f"🔎 امتیاز بازار: {item.get('market_score')}٪\n"

            )


            if item.get(
                "entry"
            ):


                message += (

                    f"💰 ورود: {item.get('entry')}\n"

                )


            if item.get(
                "tp"
            ):


                message += (

                    f"🎯 سود: {item.get('tp')}\n"

                )


            if item.get(
                "sl"
            ):


                message += (

                    f"🛑 ضرر: {item.get('sl')}\n"

                )


            message += "\n"



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در ساخت Opportunity Report"
