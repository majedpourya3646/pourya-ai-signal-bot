# core/telegram_bot_manager.py

from core.logger import logger

from core.telegram_panel import (
    get_user_status,
    get_open_positions,
    update_user_mode,
    update_notification_level,
    update_profit_share
)

from core.subscription_manager import (
    get_subscription,
    check_subscription
)

from core.admin_manager import (
    admin_dashboard
)





def main_menu():

    return [

        [
            "📊 وضعیت حساب",
            "📈 معاملات باز"
        ],

        [
            "⚙️ تنظیمات",
            "💰 اشتراک"
        ],

        [
            "🤖 حالت معامله",
            "🔔 پیام‌ها"
        ]

    ]







def admin_menu():

    return [

        [
            "👥 کاربران",
            "💵 درآمد"
        ],

        [
            "📊 وضعیت سیستم"
        ]

    ]







def format_user_status(
    telegram_id
):

    try:


        status = get_user_status(
            telegram_id
        )


        if not status:

            return "کاربر یافت نشد"



        text = f"""

🤖 Pourya Trader AI

👤 کاربر:
{status.get('username')}

⚡ حالت:
{status.get('mode')}

📊 ریسک:
{status.get('risk')}%

💰 سهم سود:
{status.get('profit_share')}%

🔔 پیام:
{status.get('notifications')}

"""

        return text



    except Exception as e:


        logger.exception(e)


        return "خطا در دریافت اطلاعات"








def format_positions():

    try:


        positions = get_open_positions()



        if not positions:

            return """

📭 معامله بازی وجود ندارد

"""



        text = """

📈 معاملات باز:

"""



        for item in positions:


            text += f"""

🪙 {item.get('symbol')}

نوع:
{item.get('side')}

قیمت ورود:
{item.get('entry')}

حجم:
{item.get('quantity')}

----------------

"""



        return text



    except Exception as e:


        logger.exception(e)


        return ""








def format_subscription(
    telegram_id
):

    try:


        sub = get_subscription(
            telegram_id
        )


        if not sub:


            return """

❌ اشتراک فعال ندارید

"""



        return f"""

💳 اشتراک:

نوع:
{sub.get('plan')}

تاریخ پایان:
{sub.get('expire')}

وضعیت:
{'فعال' if sub.get('active') else 'غیرفعال'}

"""



    except Exception as e:


        logger.exception(e)


        return ""








def handle_user_action(
    telegram_id,
    action,
    value=None
):

    try:


        if action == "AUTO":


            return update_user_mode(

                telegram_id,

                "AUTO"

            )



        elif action == "MANUAL":


            return update_user_mode(

                telegram_id,

                "MANUAL"

            )



        elif action == "BASIC_MESSAGE":


            return update_notification_level(

                telegram_id,

                "BASIC"

            )



        elif action == "DETAIL_MESSAGE":


            return update_notification_level(

                telegram_id,

                "DETAILED"

            )



        elif action == "PROFIT_SHARE":


            return update_profit_share(

                telegram_id,

                value

            )



        return False



    except Exception as e:


        logger.exception(e)


        return False








def admin_status():

    try:


        dashboard = admin_dashboard()



        return f"""

👑 Admin Dashboard

👥 کاربران:
{dashboard.get('users')}

📊 معاملات:
{dashboard.get('summary',{}).get('trades')}

💰 درآمد نرم افزار:
{dashboard.get('software_profit')}

"""



    except Exception as e:


        logger.exception(e)


        return ""
