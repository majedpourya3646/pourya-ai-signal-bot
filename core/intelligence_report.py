# core/intelligence_report.py

from core.market_intelligence import (
    run_market_intelligence
)

from core.logger import logger



def create_intelligence_report():

    try:


        data = run_market_intelligence()



        analysis = data.get(
            "analysis",
            []
        )


        pumps = data.get(
            "pumps",
            []
        )



        message = """

🧠 <b>Market Intelligence Report</b>


"""



        message += "📊 <b>سیگنال‌های هوشمند</b>\n\n"



        count = 0



        for item in analysis:


            if item.get(
                "decision"
            ) == "WAIT":


                continue



            count += 1



            message += (

                f"🪙 {item.get('symbol')}\n"

                f"📌 تصمیم: {item.get('decision')}\n"

                f"⭐ قدرت: {item.get('confidence')}٪\n"

                f"💰 ورود: {item.get('entry')}\n"

                f"🎯 TP: {item.get('tp')}\n"

                f"🛑 SL: {item.get('sl')}\n\n"

            )



        if count == 0:


            message += (

                "❌ سیگنال قدرتمند وجود ندارد\n\n"

            )



        message += "🚀 <b>پامپ‌های احتمالی</b>\n\n"



        if not pumps:


            message += (

                "❌ موردی پیدا نشد\n"

            )


        else:


            for pump in pumps[:10]:


                message += (

                    f"🔥 {pump.get('symbol')}\n"

                    f"📈 تغییر: {pump.get('change')}٪\n"

                    f"📊 قدرت: {pump.get('score')}٪\n\n"

                )



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش هوش بازار"
