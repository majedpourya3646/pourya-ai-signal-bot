# core/user_report.py

from core.user_manager import (
    get_users
)

from core.trade_history import (
    get_total_profit
)

from core.profit_share import (
    calculate_profit_share
)

from core.logger import logger



def create_user_profit_report():

    try:


        users = get_users()



        total_profit = get_total_profit()



        if not users:


            return """

👥 <b>User Report</b>


❌ هیچ کاربری ثبت نشده


🤖 Pourya Trader AI

"""



        shares = calculate_profit_share(
            total_profit
        )



        message = """

👥 <b>گزارش کاربران</b>


"""



        for item in shares:


            message += (

                f"👤 {item.get('username')}\n"

                f"💰 سود کل سیستم: {total_profit} USDT\n"

                f"💵 سهم کاربر: {item.get('share')} USDT\n\n"

            )



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش کاربران"
