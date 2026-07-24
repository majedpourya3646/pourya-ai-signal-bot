# core/profit_share.py

from core.logger import logger

from core.user_manager import (
    get_users
)



def calculate_profit_share(
    profit
):

    try:


        users = get_users()


        result = []



        for user in users:


            if not user.get(
                "active",
                False
            ):


                continue



            percentage = user.get(
                "profit_share",
                20
            )



            share = round(

                profit *

                percentage

                /

                100,

                2

            )



            result.append(

                {

                    "user_id": user.get(
                        "id"
                    ),

                    "username": user.get(
                        "username"
                    ),

                    "profit": profit,

                    "percentage": percentage,

                    "share": share

                }

            )



        return result



    except Exception as e:


        logger.exception(
            e
        )


        return []




def create_profit_report(
    profit
):

    try:


        shares = calculate_profit_share(
            profit
        )



        if not shares:


            return "❌ کاربری برای تقسیم سود وجود ندارد"



        message = """

💰 <b>Profit Share Report</b>


"""



        for item in shares:


            message += (

                f"👤 {item.get('username')}\n"

                f"📈 سود کل: {item.get('profit')} USDT\n"

                f"💵 سهم: {item.get('share')} USDT\n\n"

            )



        message += (

            "🤖 Pourya Trader AI"

        )



        return message



    except Exception as e:


        logger.exception(
            e
        )


        return "❌ خطا در گزارش تقسیم سود"
