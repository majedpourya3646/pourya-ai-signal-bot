# core/config_manager.py

from core.database_manager import (
    save_setting,
    get_setting
)

from core.logger import logger






DEFAULT_SETTINGS = {

    "risk_percent":
        1,

    "leverage":
        10,

    "paper_trading":
        True,

    "trading_mode":
        "AUTO",

    "notification_level":
        "BASIC",

    "scheduler_mode":
        "TEST",

    "trading_interval":
        300,

    "health_check_interval":
        60,

    "backup_interval":
        86400,

    "max_open_trades":
        3,

    "min_confidence":
        65

}








def ensure_config():

    try:


        for key, value in DEFAULT_SETTINGS.items():


            current = get_setting(

                key

            )



            if current is None:


                save_setting(

                    key,

                    value

                )



        logger.info(

            "CONFIG READY"

        )


        return True



    except Exception as e:


        logger.exception(e)


        return False








def set_setting(
    key,
    value
):

    try:


        return save_setting(

            key,

            value

        )



    except Exception as e:


        logger.exception(e)


        return False








def update_settings(
    settings
):

    try:


        for key, value in settings.items():


            save_setting(

                key,

                value

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def get_all_settings():

    try:


        result = {}



        for key in DEFAULT_SETTINGS:


            result[key] = get_setting(

                key,

                DEFAULT_SETTINGS[key]

            )



        return result



    except Exception as e:


        logger.exception(e)


        return {}








def get_user_setting(
    telegram_id,
    key,
    default=None
):

    try:


        return get_setting(

            f"user_{telegram_id}_{key}",

            default

        )



    except Exception as e:


        logger.exception(e)


        return default








def set_user_setting(
    telegram_id,
    key,
    value
):

    try:


        return save_setting(

            f"user_{telegram_id}_{key}",

            value

        )



    except Exception as e:


        logger.exception(e)


        return False








def trading_is_auto():

    try:


        mode = get_setting(

            "trading_mode",

            "AUTO"

        )



        return mode == "AUTO"



    except Exception as e:


        logger.exception(e)


        return False








def paper_mode():

    try:


        value = get_setting(

            "paper_trading",

            True

        )



        return str(value).lower() in [

            "true",

            "1",

            "yes"

        ]



    except Exception as e:


        logger.exception(e)


        return True
