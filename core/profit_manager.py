# core/profit_manager.py

from datetime import datetime

from core.logger import logger

from core.user_manager import (
    get_user
)





def calculate_profit_split(
    total_profit,
    user_percent=50
):

    try:


        total_profit = float(
            total_profit
        )


        user_percent = float(
            user_percent
        )



        if total_profit <= 0:


            return {


                "user_profit":

                    0,


                "software_profit":

                    0

            }



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


            "total_profit":

                round(
                    total_profit,
                    6
                ),


            "user_profit":

                round(
                    user_profit,
                    6
                ),


            "software_profit":

                round(
                    software_profit,
                    6
                )


        }



    except Exception as e:


        logger.exception(e)


        return {}








def calculate_user_trade_result(
    telegram_id,
    trade_profit
):

    try:


        user = get_user(
            telegram_id
        )


        if not user:


            percent = 50



        else:


            percent = user.get(

                "user_profit_percent",

                50

            )



        return calculate_profit_split(

            trade_profit,

            percent

        )



    except Exception as e:


        logger.exception(e)


        return {}








def create_profit_record(
    trade,
    split
):

    try:


        record = {


            "telegram_id":

                trade.get(
                    "telegram_id"
                ),


            "symbol":

                trade.get(
                    "symbol"
                ),


            "total_profit":

                split.get(
                    "total_profit"
                ),


            "user_profit":

                split.get(
                    "user_profit"
                ),


            "software_profit":

                split.get(
                    "software_profit"
                ),


            "created_at":

                datetime.utcnow()
                .isoformat()

        }



        logger.info(

            f"PROFIT RECORD {record}"

        )



        return record



    except Exception as e:


        logger.exception(e)


        return {}








def calculate_monthly_software_income(
    records
):

    try:


        total = 0



        for item in records:


            total += float(

                item.get(

                    "software_profit",

                    0

                )

            )



        return round(

            total,

            6

        )



    except Exception as e:


        logger.exception(e)


        return 0






def format_profit_message(
    result
):

    try:


        return f"""

💰 گزارش سود معامله


📈 سود کل:
{result.get('total_profit')}$


👤 سهم کاربر:
{result.get('user_profit')}$


🤖 سهم نرم افزار:
{result.get('software_profit')}$


"""



    except Exception as e:


        logger.exception(e)


        return ""
