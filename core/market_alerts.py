# core/market_alerts.py

from telegram_sender import send_message

from core.logger import logger



def send_signal_alert(
    opportunity
):

    try:


        message = f"""

🚨 <b>سیگنال جدید Pourya Trader AI</b>


🪙 ارز:
{opportunity.get('symbol')}


📊 وضعیت:
{opportunity.get('signal')}


⭐ قدرت:
{opportunity.get('confidence')}٪


💰 ورود:
{opportunity.get('entry')}


🎯 حد سود:
{opportunity.get('tp')}


🛑 حد ضرر:
{opportunity.get('sl')}


🤖 سیستم هوشمند ترید

"""



        send_message(
            message
        )



    except Exception as e:


        logger.exception(
            e
        )




def send_pump_alert(
    pump
):

    try:


        message = f"""

🚀 <b>PUMP ALERT</b>


🪙 ارز:
{pump.get('symbol')}


⭐ قدرت پامپ:
{pump.get('score')}٪


📈 تغییر:
{pump.get('change')}٪


🔥 افزایش حجم:
x{pump.get('volume_power')}


🤖 Pourya Trader AI

"""



        send_message(
            message
        )



    except Exception as e:


        logger.exception(
            e
        )




def send_system_alert(
    title,
    text
):

    try:


        send_message(

f"""

⚠️ <b>{title}</b>


{text}


🤖 Pourya Trader AI

"""

        )


    except Exception as e:


        logger.exception(
            e
        )
