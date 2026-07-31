# core/notification_manager.py

from datetime import datetime

from core.logger import logger

from core.config_manager import (
    get_setting
)

from telegram_sender import (
    send_message
)





def get_notification_mode():

    try:


        return get_setting(

            "notification_level",

            "BASIC"

        )



    except Exception as e:


        logger.exception(e)


        return "BASIC"








def format_trade_message(
    trade
):

    try:


        mode = get_notification_mode()



        basic = f"""

📊 معامله جدید


📅 تاریخ:
{datetime.now().strftime('%Y-%m-%d')}


⏰ ساعت:
{datetime.now().strftime('%H:%M')}


🪙 ارز:
{trade.get('symbol')}


📈 جهت:
{trade.get('side')}


💰 حجم خرید:
{trade.get('quantity')}


💵 قیمت:
{trade.get('entry')}


💳 مبلغ معامله:
{trade.get('amount', '-')}


"""



        if mode == "BASIC":


            return basic





        details = f"""

{basic}


🎯 حد سود:
{trade.get('tp')}


🛑 حد ضرر:
{trade.get('sl')}


⚡ اطمینان:
{trade.get('confidence')}%


⚙️ اهرم:
{trade.get('leverage')}


📝 توضیحات تکمیلی:

{trade.get('description','')}

"""



        return details



    except Exception as e:


        logger.exception(e)


        return ""








def format_closed_trade_message(
    trade
):

    try:


        pnl = float(

            trade.get(

                "pnl",

                0

            )

        )



        percent = trade.get(

            "pnl_percent",

            0

        )



        toman = trade.get(

            "pnl_toman",

            0

        )



        return f"""

✅ معامله بسته شد


🪙 ارز:
{trade.get('symbol')}


📅 تاریخ:
{datetime.now().strftime('%Y-%m-%d')}


⏰ ساعت:
{datetime.now().strftime('%H:%M')}


📌 وضعیت:
{trade.get('reason')}


💰 سود/زیان:

{pnl}$


📊 درصد:

{percent}%


🇮🇷 ریالی:

{toman}


"""



    except Exception as e:


        logger.exception(e)


        return ""








def send_trade_notification(
    trade
):

    try:


        message = format_trade_message(

            trade

        )


        return send_message(

            message

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_close_notification(
    trade
):

    try:


        message = format_closed_trade_message(

            trade

        )



        return send_message(

            message

        )



    except Exception as e:


        logger.exception(e)


        return False








def send_sms(
    message,
    phone
):

    try:


        logger.info(

            f"SMS QUEUED {phone}"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False








def send_email(
    message,
    email
):

    try:


        logger.info(

            f"EMAIL QUEUED {email}"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False








def send_multichannel_notification(
    user,
    message
):

    try:


        results = {}



        results["telegram"] = send_message(

            message

        )



        if user.get(

            "phone"

        ):


            results["sms"] = send_sms(

                message,

                user.get("phone")

            )



        if user.get(

            "email"

        ):


            results["email"] = send_email(

                message,

                user.get("email")

            )



        return results



    except Exception as e:


        logger.exception(e)


        return {}
