# core/telegram_panel.py

from core.logger import logger

from core.user_manager import (
    create_user,
    get_user,
    update_user_setting
)

from core.trade_manager import (
    get_open_trades
)

from core.config_manager import (
    get_all_settings
)




def register_user(
    telegram_id,
    username=None
):

    try:


        return create_user(

            telegram_id,

            username

        )


    except Exception as e:


        logger.exception(e)


        return False






def get_user_status(
    telegram_id
):

    try:


        user = get_user(
            telegram_id
        )


        if not user:

            return {

                "status":
                    "USER NOT FOUND"

            }



        return {


            "username":

                user.get(
                    "username"
                ),


            "mode":

                user.get(
                    "trading_mode"
                ),


            "risk":

                user.get(
                    "risk_percent"
                ),


            "leverage":

                user.get(
                    "leverage"
                ),


            "profit_share":

                user.get(
                    "user_profit_percent"
                ),


            "notifications":

                user.get(
                    "notification_level"
                )


        }



    except Exception as e:


        logger.exception(e)


        return {}






def get_open_positions():

    try:


        trades = get_open_trades()



        result = []



        for trade in trades:


            result.append(

                {

                    "symbol":

                        trade.get(
                            "symbol"
                        ),


                    "side":

                        trade.get(
                            "side"
                        ),


                    "entry":

                        trade.get(
                            "entry"
                        ),


                    "quantity":

                        trade.get(
                            "quantity"
                        )

                }

            )


        return result



    except Exception as e:


        logger.exception(e)


        return []






def update_user_mode(
    telegram_id,
    mode
):

    try:


        if mode not in [

            "AUTO",

            "MANUAL"

        ]:

            return False



        return update_user_setting(

            telegram_id,

            "trading_mode",

            mode

        )



    except Exception as e:


        logger.exception(e)


        return False






def update_notification_level(
    telegram_id,
    level
):

    try:


        if level not in [

            "BASIC",

            "DETAILED"

        ]:

            return False



        return update_user_setting(

            telegram_id,

            "notification_level",

            level

        )



    except Exception as e:


        logger.exception(e)


        return False






def update_profit_share(
    telegram_id,
    percent
):

    try:


        percent = float(
            percent
        )


        if percent < 0 or percent > 100:

            return False



        return update_user_setting(

            telegram_id,

            "user_profit_percent",

            percent

        )



    except Exception as e:


        logger.exception(e)


        return False






def system_information():

    try:


        settings = get_all_settings()



        return {


            "trading":

                settings.get(
                    "trading_enabled"
                ),


            "paper":

                settings.get(
                    "paper_trading"
                ),


            "mode":

                settings.get(
                    "trading_mode"
                )


        }



    except Exception as e:


        logger.exception(e)


        return {}
