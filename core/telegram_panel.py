# core/telegram_panel.py

from core.logger import logger

from core.user_manager import (
    get_user,
    update_user_setting
)

from core.trade_manager import (
    get_open_trades,
    get_trade_history
)

from core.subscription_manager import (
    get_subscription,
    check_subscription
)

from core.report_manager import (
    get_performance_summary
)





def main_menu():

    return {

        "buttons":[


            {

                "text":
                "📊 وضعیت معاملات",

                "action":
                "trades"

            },


            {

                "text":
                "💰 گزارش سود",

                "action":
                "profit"

            },


            {

                "text":
                "⚙️ تنظیمات",

                "action":
                "settings"

            },


            {

                "text":
                "🚀 معاملات پیشنهادی",

                "action":
                "offers"

            },


            {

                "text":
                "⭐ اشتراک",

                "action":
                "subscription"

            }


        ]

    }








def get_user_dashboard(
    telegram_id
):

    try:


        user = get_user(

            telegram_id

        )



        if not user:


            return "کاربر ثبت نشده است"



        subscription = get_subscription(

            telegram_id

        )



        stats = get_performance_summary()



        return f"""

🤖 Pourya Trader AI


👤 کاربر:

{user.get('username')}


⚙️ حالت:

{user.get('trading_mode')}


📢 پیام‌ها:

{user.get('notification_level')}


💰 سهم سود:

{user.get('user_profit_percent')}%


📈 معاملات:

{stats.get('total')}


🎯 موفقیت:

{stats.get('win_rate')}%


⭐ اشتراک:

{subscription.get('plan') if subscription else 'FREE'}

"""



    except Exception as e:


        logger.exception(e)


        return ""








def get_open_position_view():

    try:


        trades = get_open_trades()



        if not trades:


            return "معامله بازی وجود ندارد"



        message = "📊 معاملات باز:\n\n"



        for trade in trades:


            message += f"""

🪙 {trade.get('symbol')}

📈 {trade.get('side')}

💵 ورود:
{trade.get('entry')}

🎯 TP:
{trade.get('tp')}

🛑 SL:
{trade.get('sl')}


"""



        return message



    except Exception as e:


        logger.exception(e)


        return ""








def update_notification_setting(
    telegram_id,
    mode
):

    return update_user_setting(

        telegram_id,

        "notification_level",

        mode

    )








def update_trading_mode(
    telegram_id,
    mode
):

    return update_user_setting(

        telegram_id,

        "trading_mode",

        mode

    )








def update_profit_share(
    telegram_id,
    percent
):

    return update_user_setting(

        telegram_id,

        "user_profit_percent",

        percent

    )








def subscription_view(
    telegram_id
):

    try:


        active = check_subscription(

            telegram_id

        )



        subscription = get_subscription(

            telegram_id

        )



        return {


            "active":

                active,


            "subscription":

                subscription


        }



    except Exception as e:


        logger.exception(e)


        return {}
