# core/config_manager.py

import json
import os

from core.logger import logger



CONFIG_PATH = "data/settings.json"




DEFAULT_SETTINGS = {

    "trading_enabled": True,

    "emergency_mode": False,

    "paper_trading": True,

    "scheduler_mode": "TEST",

    "trading_interval": 300,


    "notification_level": "BASIC",

    "notification_channels": [

        "telegram"

    ],


    "email_enabled": False,

    "sms_enabled": False,


    "user_profit_percent": 50,


    "risk_percent": 1,


    "max_open_trades": 3,


    "leverage": 10,


    "trading_mode": "AUTO"

}




def ensure_config():

    try:


        directory = os.path.dirname(
            CONFIG_PATH
        )


        if directory and not os.path.exists(directory):

            os.makedirs(
                directory
            )



        if not os.path.exists(CONFIG_PATH):


            with open(
                CONFIG_PATH,
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



        return True



    except Exception as e:


        logger.exception(e)


        return False






def load_settings():

    try:


        ensure_config()



        with open(
            CONFIG_PATH,
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
            CONFIG_PATH,
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

    try:

        return load_settings()


    except Exception as e:


        logger.exception(e)


        return {}





def reset_settings():

    try:


        return save_settings(
            DEFAULT_SETTINGS
        )


    except Exception as e:


        logger.exception(e)


        return False
