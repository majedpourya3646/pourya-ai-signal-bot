# core/market_alerts.py

from telegram_sender import send_message

from core.logger import logger



def send_signal_alert(
    signal
):

    try:


        message = f"""

🚨 <b>سیگنال جدید بازار</b>


🪙 ارز:
{signal.get('symbol')}


📌 تصمیم:
{signal.get('decision')}


⭐ قدرت:
{signal.get('confidence')}٪


💰 ورود:
{signal.get('entry')}


🎯 حد سود:
{signal.get('tp')}


🛑 حد ضرر:
{signal.get('sl')}


🤖 Pourya Trader AI

"""



        send_message(
            message
        )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False




def send_pump_alert(
    pump
):

    try:


        message = f"""

🔥 <b>هشدار پامپ احتمالی</b>


🪙 ارز:
{pump.get('symbol')}


📈 تغییر قیمت:
{pump.get('change')}٪


📊 قدرت حجم:
{pump.get('volume_power')}x


⭐ امتیاز:
{pump.get('score')}


⚠️ بررسی قبل از ورود


🤖 Pourya Trader AI

"""



        send_message(
            message
        )


        return True



    except Exception as e:


        logger.exception(
            e
        )


        return False
