# core/config_manager.py

import json
import os

from core.logger import logger



CONFIG_FILE = "data/settings.json"



DEFAULT_SETTINGS = {

    "auto_trade": False,

    "trading_enabled": True,

    "min_confidence": 65,

    "trading_interval": 300,

    "loop_interval": 60,

    "max_open_trades": 3,

    "risk_percent": 1,

    "paper_trading": True,

    "leverage": 10,

    "min_risk_reward": 2,

    "default_tp": 5,

    "default_sl": 2

}




def load_settings():

    try:

        if not os.path.exists(
            CONFIG_FILE
        ):

            save_settings(
                DEFAULT_SETTINGS
            )

            return DEFAULT_SETTINGS.copy()



        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(
                file
            )



        updated = False



        for key, value in DEFAULT_SETTINGS.items():

            if key not in settings:

                settings[key] = value

                updated = True



        if updated:

            save_settings(
                settings
            )



        return settings



    except Exception as e:

        logger.exception(e)

        return DEFAULT_SETTINGS.copy()




def save_settings(
    settings
):

    try:

        os.makedirs(
            "data",
            exist_ok=True
        )



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

    try:

        return load_settings()


    except Exception as e:

        logger.exception(e)

        return {}
