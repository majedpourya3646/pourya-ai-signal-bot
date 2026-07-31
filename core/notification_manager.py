# core/notification_manager.py

from datetime import datetime

from core.logger import logger

from core.user_manager import (
    get_user
)





def format_basic_trade_message(
    trade
):

    try:


        return f"""

📅 تاریخ:
{datetime.now().strftime("%Y-%m-%d %H:%M")}


🪙 رمز ارز:
{trade.get('symbol')}


📌 نوع معامله:
{trade.get('side')}


📦 حجم:
{trade.get('quantity')}


💵 مبلغ معامله:
{trade.get('amount')}


📈 سود / زیان:
{trade.get('pnl_percent')}%


💰 سود / زیان ریالی:
{trade.get('pnl_toman')}

"""



    except Exception as e:


        logger.exception(e)


        return ""








def format_detailed_trade_message(
    trade
):

    try:


        return f"""

🤖 Pourya Trader AI


📅 زمان:
{datetime.now().strftime("%Y-%m-%d %H:%M")}


🪙 ارز:
{trade.get('symbol')}


📊 سیگنال:
{trade.get('signal')}


📌 جهت:
{trade.get('side')}


💵 قیمت ورود:
{trade.get('entry')}


🎯 حد سود:
{trade.get('tp')}


🛑 حد ضرر:
{trade.get('sl')}


📦 حجم:
{trade.get('quantity')}


⚡ اهرم:
{trade.get('leverage')}


📈 درصد اطمینان:
{trade.get('confidence')}%


📊 توضیح تحلیل:

{trade.get('analysis')}


"""



    except Exception as e:


        logger.exception(e)


        return ""








def calculate_profit_split(
    total_profit,
    user_percent
):

    try:


        total_profit = float(
            total_profit
        )


        user_percent = float(
            user_percent
        )



        user_profit = (

            total_profit

            *

            user_percent

            /

            100

        )



        software_profit = (

            total_profit

            -

            user_profit

        )



        return {


            "user_profit":

                round(
                    user_profit,
                    4
                ),


            "software_profit":

                round(
                    software_profit,
                    4
                )

        }



    except Exception as e:


        logger.exception(e)


        return {


            "user_profit":

                0,


            "software_profit":

                0

        }








def format_closed_trade_message(
    trade
):

    try:


        split = calculate_profit_split(

            trade.get(
                "pnl",
                0
            ),

            trade.get(
                "user_profit_percent",
                50
            )

        )



        return f"""

✅ معامله بسته شد


🪙 ارز:
{trade.get('symbol')}


📌 نتیجه:
{trade.get('reason')}


💰 سود کل معامله:
{trade.get('pnl')}$


👤 سود کاربر:
{split.get('user_profit')}$


🤖 سهم نرم افزار:
{split.get('software_profit')}$


📊 درصد سود:
{trade.get('pnl_percent')}%


"""



    except Exception as e:


        logger.exception(e)


        return ""








def get_user_notification_mode(
    telegram_id
):

    try:


        user = get_user(
            telegram_id
        )


        if not user:


            return "BASIC"



        return user.get(

            "notification_level",

            "BASIC"

        )



    except Exception as e:


        logger.exception(e)


        return "BASIC"








def create_trade_notification(
    telegram_id,
    trade
):

    try:


        mode = get_user_notification_mode(

            telegram_id

        )



        if mode == "DETAILED":


            return format_detailed_trade_message(
                trade
            )



        return format_basic_trade_message(
            trade
        )



    except Exception as e:


        logger.exception(e)


        return ""
