# core/config_manager.py

import os
import json

from core.logger import logger




CONFIG_FILE = "data/settings.json"





DEFAULT_SETTINGS = {


    # Trading

    "trading_enabled":

        True,


    "trading_mode":

        "AUTO",


    "paper_trading":

        True,


    "scheduler_mode":

        "TEST",


    "trading_interval":

        300,



    # Risk

    "risk_percent":

        1,


    "max_open_trades":

        3,


    "max_daily_loss":

        5,


    "leverage":

        10,



    # Notification

    "notification_level":

        "BASIC",


    "report_channels":

        [

            "telegram"

        ],


    "sms_enabled":

        False,


    "email_enabled":

        False,



    # Profit Sharing

    "user_profit_percent":

        50,


    "software_profit_percent":

        50,



    # Backup

    "backup_enabled":

        True,



    # Monitoring

    "monitor_interval":

        60,


    "health_check_interval":

        60,



    # Recovery

    "emergency_mode":

        False,


    # Subscription

    "subscription_required":

        False


}







def create_config_file():

    try:


        folder = os.path.dirname(
            CONFIG_FILE
        )



        if folder and not os.path.exists(
            folder
        ):


            os.makedirs(
                folder
            )



        if not os.path.exists(
            CONFIG_FILE
        ):


            with open(

                CONFIG_FILE,

                "w",

                encoding="utf-8"

            ) as file:


                json.dump(

                    DEFAULT_SETTINGS,

                    file,

                    indent=4,

                    ensure_ascii=False

                )



        return True



    except Exception as e:


        logger.exception(e)


        return False







def load_settings():

    try:


        create_config_file()



        with open(

            CONFIG_FILE,

            "r",

            encoding="utf-8"

        ) as file:


            return json.load(
                file
            )



    except Exception as e:


        logger.exception(e)


        return DEFAULT_SETTINGS






def save_settings(
    settings
):

    try:


        with open(

            CONFIG_FILE,

            "w",

            encoding="utf-8"

        ) as file:


            json.dump(

                settings,

                file,

                indent=4,

                ensure_ascii=False

            )



        return True



    except Exception as e:


        logger.exception(e)


        return False








def get_setting(
    key,
    default=None
):

    try:


        settings = load_settings()



        return settings.get(

            key,

            default

        )



    except Exception as e:


        logger.exception(e)


        return default








def update_setting(
    key,
    value
):

    try:


        settings = load_settings()



        settings[key] = value



        return save_settings(
            settings
        )



    except Exception as e:


        logger.exception(e)


        return False







def get_all_settings():

    return load_settings()








def reset_settings():

    try:


        return save_settings(

            DEFAULT_SETTINGS

        )



    except Exception as e:


        logger.exception(e)


        return False






def ensure_config():

    try:


        return create_config_file()



    except Exception as e:


        logger.exception(e)


        return False
