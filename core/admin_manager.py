# core/admin_manager.py

from core.logger import logger

from core.user_manager import (
    get_all_active_users,
    update_user_setting
)

from core.trade_manager import (
    get_trade_history
)

from core.monitoring_manager import (
    get_monitor_status
)



def get_admin_users():

    try:

        users = get_all_active_users()

        return users


    except Exception as e:

        logger.exception(e)

        return []






def get_system_summary():

    try:


        trades = get_trade_history(
            100
        )


        monitor = get_monitor_status()



        total_profit = 0

        software_profit = 0



        for trade in trades:


            if len(trade) > 12:


                try:

                    total_profit += float(
                        trade[10] or 0
                    )


                    software_profit += float(
                        trade[13] or 0
                    )


                except:

                    pass



        return {


            "users":

                len(
                    get_admin_users()
                ),


            "trades":

                len(
                    trades
                ),


            "total_profit":

                round(
                    total_profit,
                    4
                ),


            "software_profit":

                round(
                    software_profit,
                    4
                ),


            "system":

                monitor


        }



    except Exception as e:


        logger.exception(e)


        return {}








def disable_user(
    telegram_id
):

    try:


        return update_user_setting(

            telegram_id,

            "active",

            0

        )



    except Exception as e:


        logger.exception(e)


        return False






def enable_user(
    telegram_id
):

    try:


        return update_user_setting(

            telegram_id,

            "active",

            1

        )



    except Exception as e:


        logger.exception(e)


        return False






def get_platform_profit():

    try:


        trades = get_trade_history(
            1000
        )


        profit = 0



        for trade in trades:


            try:


                profit += float(

                    trade[13] or 0

                )


            except:


                continue



        return round(
            profit,
            4
        )



    except Exception as e:


        logger.exception(e)


        return 0






def admin_dashboard():

    try:


        return {


            "users":

                get_admin_users(),


            "summary":

                get_system_summary(),


            "software_profit":

                get_platform_profit()


        }



    except Exception as e:


        logger.exception(e)


        return {}
