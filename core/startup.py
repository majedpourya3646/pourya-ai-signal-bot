# core/startup.py

from telegram_sender import send_message

from coinex_api import coinex

from core.logger import logger



def startup_check():

    try:


        logger.info(
            "SYSTEM START CHECK"
        )



        balance = coinex.get_balance()



        if not balance:


            send_message(

                "❌ شروع سیستم ناموفق بود\nعدم پاسخ CoinEx"

            )


            return False



        if balance.get(
            "code"
        ) != 0:


            send_message(

                f"❌ خطای CoinEx\n{balance}"

            )


            return False



        available = balance.get(
            "data",
            []
        )



        usdt = "0"



        if available:


            usdt = available[0].get(
                "available",
                "0"
            )



        send_message(

f"""
🚀 <b>Pourya Trader AI Started</b>

🟢 اتصال CoinEx برقرار شد

💰 موجودی:
{usdt} USDT

🤖 سیستم آماده تحلیل بازار است
"""

        )



        return True



    except Exception as e:


        logger.exception(
            e
        )


        send_message(

            f"❌ Startup Error\n{e}"

        )


        return False
