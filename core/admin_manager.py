# core/admin_manager.py

from datetime import datetime

from core.logger import logger

from core.user_manager import (
    get_all_active_users,
    deactivate_user,
    activate_user
)

from core.payment_manager import (
    calculate_total_revenue
)

from core.trade_manager import (
    get_trade_history
)

from core.health_monitor import (
    get_health_status
)





def admin_dashboard():

    try:


        users = get_all_active_users()



        trades = get_trade_history()



        revenue = calculate_total_revenue()



        health = get_health_status()



        return {


            "users":

                len(users),


            "trades":

                len(trades),


            "software_profit":

                revenue,


            "health":

                health,


            "time":

                datetime.utcnow()
                .isoformat()


        }



    except Exception as e:


        logger.exception(e)


        return {}








def get_users_report():

    try:


        users = get_all_active_users()



        return {


            "count":

                len(users),


            "users":

                users


        }



    except Exception as e:


        logger.exception(e)


        return {}








def activate_account(
    telegram_id
):

    try:


        result = activate_user(

            telegram_id

        )


        logger.info(

            f"USER ACTIVATED {telegram_id}"

        )



        return result



    except Exception as e:


        logger.exception(e)


        return False








def block_account(
    telegram_id
):

    try:


        result = deactivate_user(

            telegram_id

        )


        logger.warning(

            f"USER BLOCKED {telegram_id}"

        )



        return result



    except Exception as e:


        logger.exception(e)


        return False








def format_admin_report():

    try:


        dashboard = admin_dashboard()



        return f"""

👑 Pourya Trader AI Admin


👥 کاربران فعال:

{dashboard.get('users')}


📊 تعداد معاملات:

{dashboard.get('trades')}


💰 درآمد نرم افزار:

{dashboard.get('software_profit')}$


🖥 وضعیت سیستم:

{dashboard.get('health')}


⏰ زمان:

{dashboard.get('time')}

"""



    except Exception as e:


        logger.exception(e)


        return ""








def system_control():

    try:


        return {


            "trading":

                True,


            "manual_mode":

                True,


            "auto_mode":

                True,


            "emergency":

                False


        }



    except Exception as e:


        logger.exception(e)


        return {}
