# core/config_manager.py

import json
import os

from core.logger import logger



CONFIG_FILE = "data/settings.json"



DEFAULT_SETTINGS = {

    "auto_trade": False,

    "trading_enabled": True,

    "min_confidence": 65,

    "loop_interval": 60,

    "max_open_trades": 3,

    "risk_percent": 1,

    "paper_trading": True,

    "leverage": 10

}





def load_settings():

    try:

        if not os.path.exists(
            CONFIG_FILE
        ):

            save_settings(
                DEFAULT_SETTINGS
            )


            return DEFAULT_SETTINGS



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
